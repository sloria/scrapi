# from api.webview.models import Document
# from api.webview.models import LastHarvest
#
#
# import logging
# logger = logging.getLogger(__name__)
#
#
# class LastHarvest():
#
#     def update_harvest(self):
#         sources = Document.objects.values('source').distinct()
#         print sources
#         for source in sources:
#             document = Document.objects.values(source=source).order_by('providerUpdatedDateTime')[0]
#             document_date = document.providerUpdatedDateTime
#             if LastHarvest.objects.filter(source=source).exists():
#                 most_recent = LastHarvest.objects.filter(source=source)
#                 if document_date > most_recent.last_harvest:
#                     most_recent.last_harvest = document_date
#                     most_recent.save()
#
#             else:
#                 new_source = LastHarvest(source=source, date = document_date)
#                 new_source.save()
#
#
# def main():
#     LastHarvest.get_date()
