var TIMERS = {
    one_shot: [],
    periodic: []
};

function make_timer(name, callback, timeout, one_shot) {
    var timer_id;
    if (one_shot) {
        if (name in TIMERS['one_shot']){
            clear_timer(name, true);
        }

        timer_id = window.setTimeout(callback, timeout);
        TIMERS['one_shot'][name] = timer_id;
    } else {
        if (name in TIMERS['periodic']){
            clear_timer(name, false);
        }

        timer_id = window.setInterval(callback, timeout);
        TIMERS['periodic'][name] = timer_id;
    }
    return timer_id;
}

function clear_timer(name, one_shot){
    if (one_shot){
        var timer_id = TIMERS['one_shot'][name];
        window.clearTimeout(timer_id);
        delete TIMERS['one_shot'][name];
    }else{
        var timer_id = TIMERS['periodic'][name];
        window.clearInterval(timer_id);
        delete TIMERS['periodic'][name];
    }
}

function clear_timers(){
    for (var t in TIMERS['one_shot']){
        clear_timer(t, true);
    }
    for (var t in TIMERS['periodic']){
        clear_timer(t);
    }
}