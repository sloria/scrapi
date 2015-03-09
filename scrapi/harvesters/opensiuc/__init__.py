"""
Harvester for the OpenSIUC API at Southern Illinois University for the SHARE project

More information available here:
https://github.com/CenterForOpenScience/SHARE/blob/master/providers/edu.siu.opensiuc.md

An example API call: http://opensiuc.lib.siu.edu/do/oai/?verb=ListRecords&metadataPrefix=oai_dc&from=2014-10-09T00:00:00Z
"""


from __future__ import unicode_literals

from scrapi.base import OAIHarvester


opensiuc = OAIHarvester(
    name='opensiuc',
    base_url='http://opensiuc.lib.siu.edu/do/oai/',
    property_list=['type', 'source', 'publisher', 'format',
                   'identifier', 'date', 'setSpec'],
    approved_sets=[
        'ad_pubs',
        'agecon_articles',
        'agecon_wp',
        'anat_pubs',
        'anthro_pubs',
        'arch_videos',
        'asfn_articles',
        'auto_pres',
        'ccj_articles',
        'cee_pubs',
        'chem_mdata',
        'chem_pubs',
        'cs_pubs',
        'cs_sp',
        'cwrl_fr',
        'dh_articles',
        'dh_pres',
        'dh_works',
        'dissertations',
        'ebl',
        'ece_articles',
        'ece_books',
        'ece_confs',
        'ece_tr',
        'econ_dp',
        'econ_pres',
        'epse_books',
        'epse_confs',
        'epse_pubs',
        'esh_2014',
        'fiaq_pubs',
        'fiaq_reports',
        'fin_pubs',
        'fin_wp',
        'for_articles',
        'geol_comp',
        'geol_pubs',
        'gers_pubs',
        'gmrc_gc',
        'gmrc_nm',
        'gs_rp',
        'hist_pubs',
        'histcw_pp',
        'igert_cache',
        'igert_reports',
        'ijshs_2014',
        'im_pubs',
        'jcwre',
        'kaleidoscope',
        'math_aids',
        'math_articles',
        'math_books',
        'math_diss',
        'math_grp',
        'math_misc',
        'math_theses',
        'meded_books',
        'meded_confs',
        'meded_pubs',
        'meep_articles',
        'micro_pres',
        'micro_pubs',
        'morris_articles',
        'morris_confs',
        'morris_surveys',
        'music_gradworks',
        'ojwed',
        'pb_pubs',
        'pb_reports',
        'phe_pres',
        'phe_pubs',
        'phys_pubs',
        'phys_vids',
        'pn_wp',
        'pnconfs_2010',
        'pnconfs_2011',
        'pnconfs_2012',
        'ppi_papers',
        'ppi_sipolls',
        'ppi_statepolls',
        'ps_confs',
        'ps_dr',
        'ps_pubs',
        'ps_wp',
        'psas_articles',
        'psych_diss',
        'psych_grp',
        'psych_pubs',
        'psych_theses',
        'reach_posters',
        'rehab_pubs',
        'safmusiccharts_faculty',
        'safmusiccharts_students',
        'safmusicpapers_faculty',
        'safmusicpapers_students',
        'srs_2009',
        'theses',
        'ucowrconfs_2003',
        'ucowrconfs_2004',
        'ucowrconfs_2005',
        'ucowrconfs_2006',
        'ucowrconfs_2007',
        'ucowrconfs_2008',
        'ucowrconfs_2009',
        'ugr_mcnair',
        'wed_diss',
        'wed_grp',
        'wed_theses',
        'wrd2011_keynote',
        'wrd2011_pres',
        'zool_data',
        'zool_diss',
        'zool_pubs'
    ]
)

harvest = opensiuc.harvest
normalize = opensiuc.normalize
