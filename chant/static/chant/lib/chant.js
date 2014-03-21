(function ($) {
    $.widget('chant.Chant', {
        options: {
            ws_url: 'ws://localhost:8888/',
            session_key: null,
            time_format: 'LLL:ss',
            locale: 'en',

            typing_img_size: {
                width: 16,
                height: 16
            },

            favicon_options: {
                type : 'rectangle',
                animation: 'slide'
            },

            on_message_sound_url: '/static/chant/sounds/msg',

            info_area_default_remove_timeout: 2000,
            info_area_onclose_timeout: 2000,
            info_area_onopen_timeout: 2000
        },

        _create: function () {
            this.ui_template = $('#chant-ui-template').html();
            this.ui_rooms_template = $('#chant-rooms-list-template').html();
            this.ui_message_template = $('#chant-ui-message-template').html();
            this.ui_room_container_template = $('#chant-ui-room-container-template').html();
            this.ui_typing_icon_template = $('#chant-ui-typing-icon-template').html();
            this.ui_onopen_template = $('#chant-ui-onopen-template').html();
            this.ui_onclose_template = $('#chant-ui-onclose-template').html();
            this.ui_rate_limit_template = $('#chant-ui-rate-limit-template').html();
            this.ui_error_template = $('#chant-ui-error-template').html();

            this.favicon = new Favico(this.options.favicon_options);
            this.is_visible = true;
            this.total_unread = 0;

            this.rooms = {};

            this._init_socket();
            this._init_audio();
            this._render();
        },

        _init_audio: function(){
            this.on_message_sound = new Audio();
            var mp3_support = this.on_message_sound.canPlayType('audio/mp3');
            var url = this.options.on_message_sound_url;
            if (mp3_support === 'probably' || mp3_support === 'maybe'){
                url += '.mp3';
            } else {
                url += '.ogg';
            }

            this.on_message_sound.src = url;
            this.on_message_sound.preload = 'auto';
        },

        _render: function () {
            this.element.html(this.ui_template);
            this.el_messages_container = this.element.find('.chant-messages');
            this.el_msg_form = this.element.find('.chant-send-form');
            this.el_rooms_container = this.element.find('.chant-rooms-list');
            this.el_room_filter = this.element.find('[name="room-filter"]');
            this.el_info_area = this.element.find('.info-area');

            this._init_handlers();
        },

        _init_socket: function(){
            this.ws = new WebSocket(this.options.ws_url);
            this.ws.onopen = this._onopen();
            this.ws.onmessage = this._onmessage();
            this.ws.onclose = this._onclose();
        },

        _onclose: function() {
            var chant = this;
            var onclose_handler = function(){
                var el = $(chant.ui_onclose_template);
                chant.append_info_autohide(el, 'onclose', 0, chant.options.info_area_onclose_timeout);

                make_timer('ws_reconnect', function(){
                    chant._init_socket();
                }, 1000, true);
            };
            return onclose_handler;
        },

        _onopen: function() {
            var chant = this;
            return function(){
                chant._send_authenticate();
                var el = $(chant.ui_onopen_template);
                chant.append_info_autohide(el, 'onopen', 0, chant.options.info_area_onopen_timeout);
            };
        },

        _onmessage: function() {
            var chant = this;
            return function(event){
                var data = JSON.parse(event.data);
                chant._process_message(data);
            }
        },

        _init_handlers: function() {
            var chant = this;
            chant.element.on('submit', chant.el_msg_form, function(){
                var textarea = $(this).find('[name="message"]');
                var message = textarea.val();
                if (!message){
                    return false;
                }
                chant.post_message(message);
                textarea.val('');
                return false;
            });

            chant.element.on('click', '.refresh-rooms', function(){
                chant.el_room_filter.val('');
                chant.send_update_rooms();
                return false;
            });

            chant.el_rooms_container.on('click', '.activate-room', function(e){
                if (e.skip_activate){
                    return
                }
                $(this).addClass('active');
                chant.set_active_room($(this).data('room'));
            });

            chant.el_rooms_container.on('click', '.activate-room > .btn-group', function(e){
                e.skip_activate = true;
            });

            chant.el_msg_form.keypress(function(e){
                var current_room = chant.room_id;

                if (e.which == 13 && !(e.ctrlKey || e.shiftKey)){
                    chant.el_msg_form.trigger('submit');
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    return false;
                }

                if (chant.rooms[current_room]['can_send_typing']){
                    chant.send_typing(current_room);
                    chant.rooms[current_room]['can_send_typing'] = false;
                    make_timer('send_typing_cmd', function(){
                        chant.rooms[current_room]['can_send_typing'] = true;
                    }, 1000, true);
                }

            });
            
            chant.el_room_filter.keyup(function(e){
                var filter_query = $(this).val();
                chant.el_rooms_container.find('.activate-room').removeClass('hidden');

                if (!filter_query){
                    return;
                }

                chant.el_rooms_container
                    .find('.activate-room')
                    .filter(function(){
                        return $(this).find('.room-name').text().indexOf(filter_query) == -1;
                    })
                    .addClass('hidden');
            });

            chant.el_messages_container.on('click', '.load-room-history', function(e){
                var room_id = $(this).data('room');
                var min_message_id = chant.get_room_container(room_id).find('.chant-message:first').data('pk');
                chant.send_load_history(room_id, min_message_id, 20);
                return false;
            });

            chant.el_messages_container.on('click', '.scroll-down', function(e){
                var height = chant.el_messages_container.prop('scrollHeight') + 'px';
                chant.el_messages_container.slimScroll({scrollTo: height});
                return false;
            });

            chant.element.find('.slim-scroll').each(function(){
                var el = $(this);
                el.slimScroll({
                    height: el.data('height') || 300,
                    railVisible: true
//                    allowPageScroll: true
                });
            });

            $(window).on('blur focus', function(e) {
                var prevType = $(this).data('prevType');
                if (prevType != e.type) {
                    switch (e.type) {
                        case 'blur':
                            chant.is_visible = false;
                            break;
                        case 'focus':
                            chant.is_visible = true;
                            chant.total_unread = 0;
                            chant.favicon.badge(0);
                            break;
                    }
                }
                $(this).data('prevType', e.type);
            });

        },

        _render_rooms: function(bundle) {
            var res = $.mustache(this.ui_rooms_template, bundle);
            this.el_rooms_container.html(res);
            if (this.rooms){
                var active_room = sessionStorage.getItem('chant:active-room');
                if (!(active_room*1)){
                    for (var prop in this.rooms){
                        active_room = prop;
                        break;
                    }
                }
                this.set_active_room(active_room);
            }

        },

        set_active_room: function(room_id){
            this.room_id = room_id;
            this.el_rooms_container.find('.activate-room').removeClass('active');
            this.el_rooms_container.find('[data-room="' + room_id + '"]').addClass('active');
            sessionStorage.setItem('chant:active-room', room_id);

            this.el_messages_container.find('.room-messages').addClass('hidden');

            var room_messages = this.get_room_container(room_id);
            room_messages.removeClass('hidden');
            this.set_room_unread(room_id);

        },

        set_room_unread: function(room_id, count){
            if (!this.rooms[room_id]){
                this.rooms[room_id] = {};
            }

            this.rooms[room_id]['unread'] = count || 0;
            this.el_rooms_container
                .find('[data-room="' + room_id + '"]')
                .find('.unread-count')
                .html(count || '');
        },

        get_room_container: function(room_id){
            var room_messages = this.el_messages_container.find('.room-messages[data-room="' + room_id + '"]');
            if (room_messages.length == 0){
                var el = $($.mustache(this.ui_room_container_template, {room: room_id}));
                this.el_messages_container.append(el);
            }
            return this.el_messages_container.find('.room-messages[data-room="' + room_id + '"]');
        },

        _process_message: function(bundle) {
            //console.log(bundle);
            if (bundle.result == 'error'){
                this._process_error(bundle);
            }

            switch(bundle.command){
                case 'authenticate':
                    this.send_update_rooms();
                    break;

                case 'rooms':
                    for (var i=0; i<bundle.data.length; i++){
                        var r = bundle.data[i];
                        this.rooms[r.id] = r;
                        this.rooms[r.id]['unread'] = 0;
                        this.rooms[r.id]['can_send_typing'] = true;
                    }
                    this._render_rooms(bundle);
                    break;

                case 'post':
                    this._process_post(bundle);
                    break;

                case 'history':
                    this._process_history(bundle);
                    break;

                case 'typing':
                    this._process_typing(bundle);
                    break;
            }
        },

        _process_error: function(bundle) {
            switch (bundle.reason){
                case 'rate_limit_exceeded':
                    var el = $(this.ui_rate_limit_template);
                    this.append_info_autohide(el, 'ratelimit', 0);
                    break;

                default:
                    var el = $(this.ui_error_template);
                    this.append_info_autohide(el, 'unknown', 0);
                    break;
            }
        },

        _process_typing: function(bundle){
            var data = bundle.data;
            var user = data.user;
            var room_id = data.room;

            if (this.room_id != room_id){
                return;
            }

            $.extend(data, this.options.typing_img_size);
            var img = $($.mustache(this.ui_typing_icon_template, data));
            this.append_info_autohide(img, 'typing', user.id, this.options.info_area_typing_remove_timeout);
        },

        append_info_autohide: function(el, action_name, action_id, remove_timeout){
            var chant = this;
            var selector = '[data-action="' + action_name + '"][data-id="' + action_id + '"]';
            remove_timeout = remove_timeout || this.options.info_area_default_remove_timeout;

            if (!this.el_info_area.find(selector).length){
                var wrapper = $('<div class="chant-info-wrapper"/>').attr('data-action', action_name).attr('data-id', action_id);
                wrapper.append(el);
                this.el_info_area.append(wrapper.css('display', 'inline').hide().fadeIn());
            }

            make_timer('chant_remove_info_' + action_name + '_' + action_id, function(){
                chant.el_info_area.find(selector).fadeOut(300, function(){
                    this.remove();
                });
            }, remove_timeout, true);

        },

        _process_history: function(bundle){
            var data = bundle.data;
            var room_id = data.room;
            var messages = data.messages;

            for (var i=0; i<messages.length; i++){
                var msg = messages[i];
                this.add_message(msg.room, msg);
            }
        },

        _process_post: function(bundle){
            this.add_message(bundle.data.room, bundle.data, true);
            if (!this.is_visible){
                this.favicon.badge(++this.total_unread);
                this.on_message_sound.play();
            }
        },

        add_message: function(room_id, message_data, scroll){
            var m = moment(message_data.created_at);
            message_data.created_at_localized = m.lang(this.options.locale).format(this.options.time_format);

            var new_message = $($.mustache(this.ui_message_template, message_data));
            var room_container = this.get_room_container(room_id);
            if (room_container.find('.chant-message[data-pk="' + message_data.id + '"]').length){
                return;
            }

            var inserted = false;
            room_container.find('.chant-message').each(function(){
                var current_message = $(this);
                var pk = current_message.data('pk');
                if (!inserted && message_data.id < pk){
                    new_message.fadeIn().insertBefore(current_message);
                    inserted = true;
                }
            });

            if (!inserted){
                room_container.append(new_message.fadeIn());
            }

            if (this.room_id != room_id){
                this.rooms[room_id]['unread']++;
                this.set_room_unread(room_id, this.rooms[room_id]['unread']);
            }

            if (scroll){
                var height =this.el_messages_container.prop('scrollHeight') + 'px';
                this.el_messages_container.slimScroll({scrollTo: height});
            }
        },

        post_message: function(message){
            this.send_json({
                request: 'post',
                data: {
                    message: message,
                    room: (this.room_id) * 1
                }
            });
        },

        _send_authenticate: function() {
            this.send_json({
                request: 'authenticate',
                data: this.options.session_key
            });
        },

        send_typing: function(room_id) {
            this.send_json({
                request: 'typing',
                data: {room: room_id}
            });
        },

        send_load_history: function(room_id, min_msg_id, count){
            this.send_json({
                request: 'history',
                data: {
                    room: room_id,
                    least_id: min_msg_id || null,
                    count: count
                }
            });
        },

        send_update_rooms: function(){
            this.send_json({request: 'rooms'});
        },

        send_json: function(data) {
            var json_data = JSON.stringify(data);
            this.ws.send(json_data);
        },

        setOption: function (key, value) {
            if (value != undefined) {
                this.options[key] = value;
                this._render();
                return this;
            }
            else {
                return this.options[key];
            }
        }
    })
})(jQuery);