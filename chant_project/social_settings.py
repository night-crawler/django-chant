AUTHENTICATION_BACKENDS = (
    'social.backends.amazon.AmazonOAuth2',
    'social.backends.angel.AngelOAuth2',
    'social.backends.aol.AOLOpenId',
    'social.backends.appsfuel.AppsfuelOAuth2',
    'social.backends.behance.BehanceOAuth2',
    'social.backends.belgiumeid.BelgiumEIDOpenId',
    'social.backends.bitbucket.BitbucketOAuth',
    'social.backends.box.BoxOAuth2',
    'social.backends.clef.ClefOAuth2',
    'social.backends.coinbase.CoinbaseOAuth2',
    'social.backends.dailymotion.DailymotionOAuth2',
    'social.backends.disqus.DisqusOAuth2',
    'social.backends.douban.DoubanOAuth2',
    'social.backends.dropbox.DropboxOAuth',
    'social.backends.evernote.EvernoteSandboxOAuth',
    'social.backends.facebook.FacebookAppOAuth2',
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.fedora.FedoraOpenId',
    'social.backends.fitbit.FitbitOAuth',
    'social.backends.flickr.FlickrOAuth',
    'social.backends.foursquare.FoursquareOAuth2',
    'social.backends.github.GithubOAuth2',
    'social.backends.google.GoogleOAuth',
    'social.backends.google.GoogleOAuth2',
    'social.backends.google.GoogleOpenId',
    'social.backends.google.GooglePlusAuth',
    'social.backends.instagram.InstagramOAuth2',
    'social.backends.jawbone.JawboneOAuth2',
    'social.backends.linkedin.LinkedinOAuth',
    'social.backends.linkedin.LinkedinOAuth2',
    'social.backends.live.LiveOAuth2',
    'social.backends.livejournal.LiveJournalOpenId',
    'social.backends.mailru.MailruOAuth2',
    'social.backends.mendeley.MendeleyOAuth',
    'social.backends.mendeley.MendeleyOAuth2',
    'social.backends.mixcloud.MixcloudOAuth2',
    'social.backends.odnoklassniki.OdnoklassnikiOAuth2',
    'social.backends.open_id.OpenIdAuth',
    'social.backends.openstreetmap.OpenStreetMapOAuth',
    'social.backends.orkut.OrkutOAuth',
    'social.backends.persona.PersonaAuth',
    'social.backends.podio.PodioOAuth2',
    'social.backends.rdio.RdioOAuth1',
    'social.backends.rdio.RdioOAuth2',
    'social.backends.readability.ReadabilityOAuth',
    'social.backends.reddit.RedditOAuth2',
    'social.backends.runkeeper.RunKeeperOAuth2',
    'social.backends.skyrock.SkyrockOAuth',
    'social.backends.soundcloud.SoundcloudOAuth2',
    'social.backends.stackoverflow.StackoverflowOAuth2',
    'social.backends.steam.SteamOpenId',
    'social.backends.stocktwits.StocktwitsOAuth2',
    'social.backends.stripe.StripeOAuth2',
    'social.backends.suse.OpenSUSEOpenId',
    'social.backends.thisismyjam.ThisIsMyJamOAuth1',
    'social.backends.trello.TrelloOAuth',
    'social.backends.tripit.TripItOAuth',
    'social.backends.tumblr.TumblrOAuth',
    'social.backends.twilio.TwilioAuth',
    'social.backends.twitter.TwitterOAuth',
    'social.backends.vk.VKOAuth2',
    'social.backends.weibo.WeiboOAuth2',
    'social.backends.xing.XingOAuth',
    'social.backends.yahoo.YahooOAuth',
    'social.backends.yahoo.YahooOpenId',
    'social.backends.yammer.YammerOAuth2',
    'social.backends.yandex.YandexOAuth2',
    'social.backends.vimeo.VimeoOAuth1',
    'social.backends.email.EmailAuth',
    'social.backends.username.UsernameAuth',
    'django.contrib.auth.backends.ModelBackend',
)


LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/done/'
SOCIAL_AUTH_STRATEGY = 'social.strategies.django_strategy.DjangoStrategy'
SOCIAL_AUTH_STORAGE = 'social.apps.django_app.default.models.DjangoStorage'
SOCIAL_AUTH_GOOGLE_OAUTH_SCOPE = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/userinfo.profile'
]


# SOCIAL_AUTH_EMAIL_FORM_HTML = 'email_signup.html'
# SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'example.app.mail.send_validation'
# SOCIAL_AUTH_EMAIL_VALIDATION_URL = '/email-sent/'
# SOCIAL_AUTH_USERNAME_FORM_HTML = 'username_signup.html'

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'common.pipeline.require_email',
    'social.pipeline.mail.mail_validation',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details'
)


