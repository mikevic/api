from django.urls import path
from .views import index, ping, actioninfo, eventinfo, stationinfo, estimate, reset, importcsv

urlpatterns = [
    path('',index),
    path('info',index),
    path('info/actions',index),
    path('info/action/<action>', actioninfo ),
    path('info/events', eventinfo ),
    path('info/event/<event>', eventinfo ),
    path('info/stations', stationinfo ),
    path('info/station/<station>', stationinfo ),
    path('estimate/<action>', estimate ),
    path('reset', reset ),
    path('import', importcsv )

]