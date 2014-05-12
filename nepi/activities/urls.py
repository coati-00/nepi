from django.conf.urls.defaults import patterns
'''Want to switch to class based views but not sure how'''
from nepi.activities.views import CreateConversationView
from nepi.activities.views import UpdateConversationView
from nepi.activities.views import DeleteConversationView
from nepi.activities.views import ScenarioListView
from nepi.activities.views import ScenarioDetailView
from nepi.activities.views import ScenarioDeleteView
#from nepi.activities.views import get_click


urlpatterns = patterns(
    '',
    (r'^create_conversation/$', CreateConversationView.as_view()),
    (r'^update_conversation/(?P<pk>\d+)/$', UpdateConversationView.as_view()),
    (r'^delete_conversation/(?P<pk>\d+)/$', DeleteConversationView.as_view()),

    (r'^classview_scenariolist/$', ScenarioListView.as_view()),
    (r'^delete_scenario/(?P<pk>\d+)/$', ScenarioDeleteView.as_view()),
    (r'^scenario_display/(?P<pk>\d+)/$', ScenarioDetailView.as_view()),
    (r'^get_click/$', 'nepi.activities.views.get_click'),
)
