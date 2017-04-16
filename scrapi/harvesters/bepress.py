from __future__ import unicode_literals
from scrapi.base import OAIHarvester


class DigitalcommonsAcuHarvester(OAIHarvester):
    short_name = 'digitalcommons.acu'
    long_name = 'Digital Commons @ ACU'
    url = 'http://digitalcommons.acu.edu/do/oai/'

    base_url = 'http://digitalcommons.acu.edu/do/oai/'
    property_list = ['rights', 'format', 'source', 'date', 'identifier', 'type']
    timezone_granularity = True


class DigitalcommonsAmericanHarvester(OAIHarvester):
    short_name = 'digitalcommons.wcl.american'
    long_name = 'Digital Commons @ American University Washington College of Law'
    url = 'http://digitalcommons.wcl.american.edu/do/oai/'

    base_url = 'http://digitalcommons.wcl.american.edu/do/oai/'
    property_list = ['date', 'source', 'identifier', 'type', 'format']
    timezone_granularity = True


class jevohealthHarvester(OAIHarvester):
    short_name = 'jevohealth'
    long_name = 'Journal of Evolution and Health'
    url = 'http://jevohealth.com/do/oai/'

    base_url = 'http://jevohealth.com/do/oai/'
    property_list = ['date', 'source', 'identifier', 'type', 'format']
    timezone_granularity = True


class AuraAntiochHarvester(OAIHarvester):
    short_name = 'aura.antioch'
    long_name = 'AURA - Antioch University Repository and Archive'
    url = 'http://aura.antioch.edu/do/oai/'

    base_url = 'http://aura.antioch.edu/do/oai/'
    property_list = ['date', 'source', 'identifier', 'type', 'format']
    timezone_granularity = True


class ScholarworksArcadiaHarvester(OAIHarvester):
    short_name = 'scholarworks.arcadia'
    long_name = 'ScholarWorks@Arcadia'
    url = 'http://scholarworks.arcadia.edu/do/oai/'

    base_url = 'http://scholarworks.arcadia.edu/do/oai/'
    property_list = ['date', 'source', 'identifier', 'type', 'format']
    timezone_granularity = True
