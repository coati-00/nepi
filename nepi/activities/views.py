    # Create your views here.
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
import json
from nepi.activities.models import (
    Conversation, ConversationScenario,
    ConvClick, ConversationResponse,
    ConversationForm, RetentionRateCard,
    RetentionClick, RetentionResponse)
from django.views.generic import View
from django.utils.decorators import method_decorator


def ajax_required(func):
    """
    AJAX request required decorator
    use it in your views:
    @ajax_required
    def my_view(request):
    """

    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseNotAllowed("")
        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap


class JSONResponseMixin(object):
    @method_decorator(ajax_required)
    def dispatch(self, *args, **kwargs):
        return super(JSONResponseMixin, self).dispatch(*args, **kwargs)

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return HttpResponse(json.dumps(context),
                            content_type='application/json',
                            **response_kwargs)


# but I don't really need and ajax thanks view...
class ThanksView(View):
    '''We need a generic thanks view to pop up
    when appropriate and then refresh the page.'''
    def get(self, request):
        return render('thanks.html')


class CreateConverstionView(CreateView):
    template_name = 'activities/add_conversation.html'
    form_class = ConversationForm
    fields = ['text_one', 'response_one',
              'response_two', 'response_three', 'complete_dialog']
    success_url = '/pages/main/edit/'

    def form_valid(self, form):
        nc = Conversation.objects.create()
        nc.scenario_type = form.cleaned_data['scenario_type']
        path_split = self.request.path.split('/')
        key = path_split[3]
        scenario = ConversationScenario.objects.get(pk=key)
        if nc.scenario_type == 'G':
            scenario.good_conversation = nc
            scenario.save()
        elif nc.scenario_type == 'B':
            scenario.bad_conversation = nc
            scenario.save()

        nc.text_one = form.cleaned_data['text_one']
        nc.response_one = form.cleaned_data['response_one']
        nc.response_two = form.cleaned_data['response_two']
        nc.response_three = form.cleaned_data['response_three']
        nc.complete_dialog = form.cleaned_data['complete_dialog']
        nc.save()
        return HttpResponseRedirect('/pages/main/edit/')


def render_to_json_response(context, **response_kwargs):
    data = json.dumps(context)
    response_kwargs['content_type'] = 'application/json'
    return HttpResponse(data, **response_kwargs)


class ScenarioListView(ListView):
    template_name = "activities/class_scenario_list_view.html"
    model = ConversationScenario


class ScenarioDetailView(DetailView):
    template_name = "activities/class_scenario_list_view.html"
    model = ConversationScenario


class ScenarioDeleteView(DeleteView):
    model = ConversationScenario
    success_url = '../../../activities/classview_scenariolist/'


class CreateConversationView(CreateView):
    model = Conversation
    template_name = 'activities/add_conversation.html'
    success_url = '/pages/main/edit/'


class UpdateConversationView(UpdateView):
    model = Conversation
    template_name = 'activities/add_conversation.html'
    fields = ['text_one', 'response_one',
              'response_two', 'response_three',
              'complete_dialog']
    success_url = '/pages/main/edit/'


class DeleteConversationView(DeleteView):
    model = Conversation
    success_url = '../../../activities/classview_scenariolist/'


class SaveResponse(View, JSONResponseMixin):
    def post(self, request):
        scenario = get_object_or_404(ConversationScenario,
                                     pk=request.POST['scenario'])
        conversation = get_object_or_404(Conversation,
                                         pk=request.POST['conversation'])
        conclick = ConvClick.objects.create(conversation=conversation)
        conclick.save()
        rs, created = ConversationResponse.objects.get_or_create(
            conv_scen=scenario, user=request.user)
        if rs.first_click is None:
            rs.first_click = conclick
            rs.save()
        elif rs.first_click is not None and rs.second_click is None:
            rs.second_click = conclick
            rs.third_click = conclick
            rs.save()
        elif rs.second_click is not None:
            rs.third_click = conclick
            rs.save()
        return render_to_json_response({'success': True})


class LastResponse(View, JSONResponseMixin):
    '''Should this be a create view?'''
    def post(self, request):
        scenario = get_object_or_404(ConversationScenario,
                                     pk=request.POST['scenario'])
        try:
            cresp = ConversationResponse.objects.get(
                user=request.user, conv_scen=scenario)
            if cresp.third_click is not None:
                return render_to_json_response(
                    {'success': True,
                     'last_conv':
                     cresp.third_click.conversation.scenario_type})
            elif (cresp.first_click is not None
                  and cresp.second_click is None):
                    return render_to_json_response(
                        {'success': True,
                         'last_conv':
                         cresp.first_click.conversation.scenario_type})

        except ConversationResponse.DoesNotExist:
            return render_to_json_response({'success': False})


class CreateCalendar(CreateView):
    model = Conversation
    template_name = 'activities/add_conversation.html'
    success_url = '/pages/main/edit/'


class SaveRetentionResponse(View, JSONResponseMixin):
    '''There must be a way to make a simple short generic method'''

    def compare_strings(self, retresponse, click_string, click_reference):
        # print "inside compare_strings"
        # print retresponse
        # print click_string
        # print click_reference
        click_saved = getattr(retresponse, click_string)
        # print click_saved
        if click_saved is None:
            print "click save is none"
            retresponse.click_saved = click_reference
            retresponse.click_saved.save()
            click_reference.save()
            return render_to_json_response({'success': True})
        elif click_saved is not None:
            print "click_save is not none"
            '''We can assume that this attribute already has a value'''
            return render_to_json_response({'success': True})

    def post(self, request):
        # print "inside post"
        # print request.POST['click_string']
        # print request.POST['retention_id']
        acceptable_clicks = ["cohort_click", "start_date_click",
                             "eligible_click", "delivery_date_click",
                             "dec_click", "jan_click", "feb_click",
                             "mar_click", "apr_click", "may_click",
                             "jun_click"]
        # print acceptable_clicks
        retention = get_object_or_404(RetentionRateCard,
                                      pk=request.POST['retention_id'])
        # print retention
        click_string = request.POST['click_string']
        # print click_string
        if click_string in acceptable_clicks:
            # print "click_string found in acceptable_clicks"
            retentionclick = RetentionClick.objects.create(
                click_string=click_string)
            #print str(retentionclick)
            rr, created = RetentionResponse.objects.get_or_create(
                retentionrate=retention, user=request.user)
            #print str(rr)
            return self.compare_strings(rr, click_string, retentionclick)
        else:
            '''If submitted string is not in the acceptable strings list
            something is very funny.'''
            return render_to_json_response({'success': False})
