"""
BSD 3-Clause License

Copyright (c) 2018, North Carolina State University
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. The names "North Carolina State University", "NCSU" and any trade‐name,
   personal name, trademark, trade device, service mark, symbol, image, icon,
   or any abbreviation, contraction or simulation thereof owned by North
   Carolina State University must not be used to endorse or promoteproducts
   derived from this software without prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import json
import os

from celery.task.control import revoke
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.views import generic
from rest_framework.response import Response
from rest_framework.views import APIView

from mortar import forms, models, tasks, utils


class ConfigureBaseView(LoginRequiredMixin, generic.TemplateView):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        analysis = self.analysis
        analysis.crawler = self.crawler
        analysis.mindmap = self.mindmap
        analysis.query = self.query

        analysis.crawler_configured = self.crawler.seed_list.exists()
        analysis.query_configured = self.query.parts.exists()
        analysis.save()

        context['analysis'] = analysis

        return context

    @cached_property
    def analysis(self):
        return models.Analysis.objects.get_or_create(id=0)[0]

    @cached_property
    def source(self):
        return models.ElasticIndex.objects.get_or_create(name='source')[0]

    @cached_property
    def dest(self):
        return models.ElasticIndex.objects.get_or_create(name='dest')[0]

    @cached_property
    def crawler(self):
        return models.Crawler.objects.get_or_create(
            name='default',
            category='web',
            index=self.source,
        )[0]

    @cached_property
    def mindmap(self):
        return models.Tree.objects.get_or_create(
            name="default",
            slug="default",
            doc_source_index=self.source,
            doc_dest_index=self.dest,
        )[0]

    @cached_property
    def query(self):
        return models.Query.objects.get_or_create(name='default', category=0)[0]


class ConfigureView(ConfigureBaseView):

    def dispatch(self, request, *args, **kwargs):
        if self.analysis.query_configured:
            return redirect(reverse('configure-query'))
        if self.analysis.dicts_configured:
            return redirect(reverse('configure-query'))
        if self.analysis.mindmap_configured:
            return redirect(reverse('configure-dictionaries'))
        if self.analysis.crawler_configured:
            return redirect(reverse('configure-mindmap'))
        return redirect(reverse('configure-crawler'))


class ConfigureCrawlerView(ConfigureBaseView):
    template_name = 'mortar/configure/crawler.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'crawler': self.crawler,
            'seed_list': [
                [seed.urlseed.url, seed.pk]
                for seed in self.crawler.seed_list.all()
            ],
            'form': forms.CrawlerForm(),
        })
        return context


class ConfigureMindMapView(ConfigureBaseView):
    template_name = 'mortar/configure/mindmap.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tree_json, flat_tree = utils.get_json_tree(self.mindmap.nodes.all())
        context.update({
            'mindmap': self.mindmap,
            'tree_json': json.dumps(tree_json),
            'tree_list': json.dumps(flat_tree),
            'form': forms.MindMapForm(),
        })
        return context

    def post(self, request, *args, **kwargs):
        self.analysis.mindmap_configured = True
        self.analysis.save()

        return redirect(reverse('configure-dictionaries'))


class ConfigureDictionariesView(ConfigureBaseView):
    template_name = 'mortar/configure/dictionaries.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'dict_path': os.path.join(settings.BASE_DIR, settings.DICTIONARIES_PATH),
            'dictionaries': models.Dictionary.objects.all(),
            'dict_list': utils.get_dict_list(),
            'has_system_dicts': os.path.isdir(settings.DICTIONARIES_PATH),
            'form': forms.DictionaryForm(),
        })
        return context

    def post(self, request, *args, **kwargs):
        self.analysis.dicts_configured = True
        self.analysis.save()

        return redirect(reverse('configure-query'))


class ConfigureQueryView(ConfigureBaseView):
    template_name = 'mortar/configure/query.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'query': self.query,
        })
        return context


class AnalyzeView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'mortar/execute.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        analysis = get_object_or_404(models.Analysis, id=0)
        context['analysis'] = analysis
        return context


class AnalysisStatus(LoginRequiredMixin, APIView):
    def get(self, request, *args, **kwargs):
        analysis = get_object_or_404(models.Analysis, pk=self.kwargs.get('pk'))
        crawler = analysis.crawler
        mindmap = analysis.mindmap
        query = analysis.query
        # es = settings.ES_CLIENT

        annotation_count = models.Annotation.objects.using('explorer').filter(query_id=query.id).count()
        return Response(json.dumps({
            'analysis': analysis.pk,
            'any_running': analysis.any_running,
            'all_finished': analysis.all_finished,
            'crawler': {
                'running': analysis.crawler_running,
                'status': crawler.status,
                'count': crawler.count,
                'errors': list(map(str, crawler.errors)),
            },
            'preprocess': {
                'running': analysis.preprocess_running,
                'status': 0 if mindmap.process_id else 1,
                'n_processed': mindmap.n_processed,
                'n_total': mindmap.n_total,
                'errors': list(map(str, mindmap.errors)),
            },
            'query': {
                'running': analysis.query_running,
                'status': query.status,
                'count': annotation_count,
                'errors': list(map(str, query.errors)),
            },
        }))


class StartAnalysis(LoginRequiredMixin, APIView):
    def post(self, request, *args, **kwargs):
        analysis = get_object_or_404(models.Analysis.objects, pk=self.kwargs.get('pk'))
        if analysis.all_configured:
            if not analysis.any_running:

                # Chain together tasks, so if crawler is killed manually, the
                # other tasks proceed after.
                chain = \
                    tasks.run_crawler.signature((analysis.crawler.pk, ), immutable=True) \
                    | tasks.preprocess.signature((analysis.mindmap.pk, ), immutable=True) \
                    | tasks.run_query.signature((analysis.query.pk, ), immutable=True)
                chain()

            return redirect('analyze')
        else:
            return redirect('configure')


class StopAnalysis(LoginRequiredMixin, APIView):
    def post(self, request, *args, **kwargs):
        analysis = get_object_or_404(models.Analysis, pk=self.kwargs.get('pk'))
        analysis.stop()
        return redirect('analyze')


class ClearResults(LoginRequiredMixin, APIView):
    def post(self, request, *args, **kwargs):
        analysis = get_object_or_404(models.Analysis, pk=self.kwargs.get('pk'))
        analysis.clear_results()
        return redirect('analyze')


class StartCrawler(LoginRequiredMixin, APIView):
    def post(self, request, *args, **kwargs):
        crawler = get_object_or_404(models.Crawler, pk=self.kwargs.get('pk'))
        if not crawler.process_id:
            tasks.run_crawler.delay(crawler.pk)
        return redirect('analyze')


class StopCrawler(LoginRequiredMixin, APIView):
    def post(self, request, *args, **kwargs):
        crawler = get_object_or_404(models.Crawler, pk=self.kwargs.get('pk'))
        if crawler.process_id:
            revoke(crawler.process_id, terminate=True)
            crawler.process_id = None
            crawler.save()
        return redirect('analyze')


class StartPreprocess(LoginRequiredMixin, APIView):
    def post(self, request, *args, **kwargs):
        mindmap = get_object_or_404(models.Tree, pk=self.kwargs.get('pk'))
        if not mindmap.process_id:
            tasks.preprocess.delay(mindmap.pk)
        return redirect('analyze')


class StopPreprocess(LoginRequiredMixin, APIView):
    def post(self, request, *args, **kwargs):
        mindmap = get_object_or_404(models.Tree, pk=self.kwargs.get('pk'))
        if mindmap.process_id:
            revoke(mindmap.process_id)
            mindmap.process_id = None
            mindmap.save()
        return redirect('analyze')


class StartQuery(LoginRequiredMixin, APIView):
    def post(self, request, *args, **kwargs):
        query = get_object_or_404(models.Query, pk=self.kwargs.get('pk'))
        if not query.process_id:
            tasks.run_query.delay(query.pk)
        return redirect('analyze')


class StopQuery(LoginRequiredMixin, APIView):
    def post(self, request, *args, **kwargs):
        query = get_object_or_404(models.Query, pk=self.kwargs.get('pk'))
        if query.process_id:
            revoke(query.process_id)
            query.process_id = None
            query.save()
        return redirect('analyze')


class UploadMindMapApi(LoginRequiredMixin, APIView):
    def post(self, request, *args, **kwargs):
        mindmap = get_object_or_404(models.Tree, pk=self.kwargs.get('pk'))
        if request.FILES.get('file'):
            utils.read_mindmap(mindmap, request.FILES['file'].read())
            utils.associate_tree(mindmap)
        return redirect('configure-mindmap')


class EditNodeApi(LoginRequiredMixin, APIView):
    def post(self, request, *args, **kwargs):
        node = get_object_or_404(models.Node, pk=self.kwargs.get('pk'))
        node.name = request.POST.get('name')
        node.regex = request.POST.get('regex')
        node.save()
        return redirect('configure-mindmap')


class DeleteNodeApi(LoginRequiredMixin, APIView):
    def get(self, request, *args, **kwargs):
        node = get_object_or_404(models.Node, pk=self.kwargs.get('pk'))
        node.delete()
        if not models.Node.objects.all():
            analysis = get_object_or_404(models.Analysis, id=0)
            analysis.mindmap_configured = False
            analysis.save()
        return redirect('configure-mindmap')


class AddSeedsApi(LoginRequiredMixin, APIView):
    def post(self, request, *args, **kwargs):
        crawler = get_object_or_404(models.Crawler, pk=self.kwargs.get('pk'))
        seeds = request.POST.get('seed_list').split('\n')
        for seed in seeds:
            if len(seed):
                useed, created = models.URLSeed.objects.get_or_create(url=seed.strip())
                crawler.seed_list.add(useed)
        return redirect('configure-crawler')


class EditSeedApi(LoginRequiredMixin, APIView):
    def post(self, request, *args, **kwargs):
        seed = get_object_or_404(models.URLSeed, pk=self.kwargs.get('pk'))
        seed.url = request.POST.get('url')
        seed.save()
        return redirect('configure-crawler')


class DeleteSeedApi(LoginRequiredMixin, APIView):
    def get(self, request, *args, **kwargs):
        seed = get_object_or_404(models.URLSeed, pk=self.kwargs.get('pk'))
        seed.delete()
        return redirect('configure-crawler')


class AddDictionaryApi(LoginRequiredMixin, APIView):
    def post(self, request, *args, **kwargs):
        name = request.POST.get('dict_name')
        words = request.POST.get('words').split('\n')
        clean = [word.replace("&#13;", '').replace('&#10;', '').strip() for word in words]
        d_words = '\n'.join(clean)
        new_dict = models.Dictionary.objects.create(
            name=name,
            words=d_words,
            filepath=os.sep.join([settings.DICTIONARIES_PATH, slugify(name) + ".txt"]),
        )
        new_dict.save()
        es = settings.ES_CLIENT
        es.indices.create(index='dictionaries', ignore=400)
        es.create(index="dictionaries", doc_type="dictionary", id=new_dict.id, body={'name': new_dict.name, 'words': new_dict.words.split("\n")})  # noqa
        return redirect('configure-dictionaries')


class EditDictionaryApi(LoginRequiredMixin, APIView):
    def post(self, request, *args, **kwargs):
        dic = get_object_or_404(models.Dictionary, pk=self.kwargs.get('pk'))

        words = request.POST.get('words').split('\n')
        clean = [word.replace("&#13;", '').replace('&#10;', '').strip() for word in words]
        dic.words = '\n'.join(clean)
        dic.save()
        es = settings.ES_CLIENT
        es.indices.create(index="dictionaries", ignore=400)
        es.update(index="dictionaries", doc_type="dictionary", id=dic.id, body={'doc': {'name': dic.name, 'words': dic.words.split("\n")}})  # noqa
        return redirect('configure-dictionaries')


class DeleteDictionaryApi(LoginRequiredMixin, APIView):
    def get(self, request, *args, **kwargs):
        dic = get_object_or_404(models.Dictionary, pk=self.kwargs.get('pk'))
        dic_id = dic.id
        dic.delete()
        if not models.Dictionary.objects.all():
            analysis, created = models.Analysis.objects.get_or_create(id=0)
            analysis.dicts_configured = False
            analysis.save()
        es = settings.ES_CLIENT
        es.indices.create(index="dictionaries", ignore=400)
        es.delete(index="dictionaries", doc_type="dictionary", id=dic_id)
        return redirect('configure-dictionaries')


class DictionaryUpdateView(LoginRequiredMixin, APIView):
    def get(self, request, *args, **kwargs):
        tasks.sync_dictionaries.delay()
        return redirect('configure-dictionaries')


class Home(generic.TemplateView):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        analysis, created = models.Analysis.objects.get_or_create(pk=0)
        if not analysis.all_configured:
            return redirect('configure')
        else:
            return redirect('analyze')


analyze = AnalyzeView.as_view()
start_analysis = StartAnalysis.as_view()
stop_analysis = StopAnalysis.as_view()
clear_results = ClearResults.as_view()
analysis_status = AnalysisStatus.as_view()
start_crawler = StartCrawler.as_view()
stop_crawler = StopCrawler.as_view()
start_preprocess = StartPreprocess.as_view()
stop_preprocess = StopPreprocess.as_view()
start_query = StartQuery.as_view()
stop_query = StopQuery.as_view()
edit_seed = EditSeedApi.as_view()
delete_seed = DeleteSeedApi.as_view()
edit_node = EditNodeApi.as_view()
delete_node = DeleteNodeApi.as_view()
edit_dict = EditDictionaryApi.as_view()
delete_dict = DeleteDictionaryApi.as_view()
add_dict = AddDictionaryApi.as_view()
add_seeds = AddSeedsApi.as_view()
upload_mindmap = UploadMindMapApi.as_view()
update_dictionaries = DictionaryUpdateView.as_view()
home = Home.as_view()
