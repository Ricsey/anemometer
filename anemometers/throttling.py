from rest_framework.throttling import UserRateThrottle

class WindReadingSubmitThrottle(UserRateThrottle):
    scope='windreading_submit'