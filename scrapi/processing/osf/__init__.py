from scrapi.settings import MANIFESTS
from scrapi.processing.osf import crud
from scrapi.processing.osf import collision
from scrapi.processing.base import BaseProcessor


class OSFProcessor(BaseProcessor):
    NAME = 'osf'

    def process_normalized(self, raw_doc, normalized):
        found, _hash = collision.already_processed(raw_doc)

        if found:
            return

        normalized['meta'] = {
            'docHash': _hash
        }

        try:
            normalized['collisionCategory'] = crud.get_collision_cat(normalized['source'])
        except KeyError:
            # add a collision cat of 5 for pushed docs
            normalized['collisionCategory'] = 5

        # unwrapping the normalizedDocument so that it's
        # a dictiorary from here on out
        report_norm = normalized.attributes
        resource_norm = crud.clean_report(normalized.attributes)

        report_hash = collision.generate_report_hash_list(report_norm)
        resource_hash = collision.generate_resource_hash_list(resource_norm)

        resource = collision.detect_collisions(resource_hash, is_resource=True)

        if not resource:
            resource_norm['isResource'] = True
            resource = crud.dump_metadata(resource_norm)
        else:
            # done because of a conflict of contributors format in the OSF
            del resource['contributors']

        report_norm['meta']['uids'] = report_hash
        report_norm['attached'] = {
            'pmid': resource['_id']
        }

        report = crud.dump_metadata(report_norm)

        if not resource.get('attached'):
            resource['attached'] = {}

        if resource['attached'].get('cmids'):
            resource['attached']['cmids'] += [report['_id']]
        else:
            resource['attached']['cmids'] = [report['_id']]

        if not resource.get('links'):
            resource['links'] = []

        try:
            long_name = MANIFESTS[report['source']]['longName']
        except KeyError:
            long_name = report['source']

        resource['links'].append({
            'shortName': report['source'],
            'longName': long_name,
            'url': report['id']['url']
        })


        resource['meta']['uids'] = list(set(resource['meta'].get('uids', []) + resource_hash))

        crud.update_metadata(resource['_id'], resource)
