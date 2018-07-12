import unittest
import pandas as pd
from reportcompiler_ic_tools.tables import generate_table_data
from copy import deepcopy
from pprint import pprint


class LatexTablesTest(unittest.TestCase):
    """ """

    def setUp(self):
        self.data = pd.DataFrame(
            {
                'country':
                    ['Spain', 'France', 'Germany'],
                'prevalence':
                    ['10\%', '20\%', '30\%']
            },
            index=[0, 1, 2])

        self.sample_refs = {
                'sources': {
                    'global': pd.DataFrame(),
                    'row': pd.DataFrame(),
                    'column': pd.DataFrame(),
                    'cell': pd.DataFrame(),
                },
                'notes': {
                    'global': pd.DataFrame(),
                    'row': pd.DataFrame(),
                    'column': pd.DataFrame(),
                    'cell': pd.DataFrame(),
                },
                'methods': {
                    'global': pd.DataFrame(),
                    'row': pd.DataFrame(),
                    'column': pd.DataFrame(),
                    'cell': pd.DataFrame(),
                },
                'years': {
                    'global': pd.DataFrame(),
                    'row': pd.DataFrame(),
                    'column': pd.DataFrame(),
                    'cell': pd.DataFrame(),
                },
            }

    def test_global_sources(self):
        df = {'data': self.data}
        refs = self.sample_refs

        refs['sources']['global'] = pd.DataFrame([
            {'text': 'This is a global source.'},
        ])

        df.update(refs)
        refed_data, ref_list = generate_table_data(df,
                                                   column_names=[
                                                    'Country',
                                                    'HPV prevalence'
                                                    ])

        expected_data = df['data']
        expected_data.columns = ['Country', 'HPV prevalence']
        expected_reference_list = [
            ('1', 'This is a global source.')
        ]
        pd.testing.assert_frame_equal(refed_data, expected_data)
        self.assertEqual(ref_list, expected_reference_list)

    def test_column_sources(self):
        df = {'data': self.data}
        refs = self.sample_refs

        refs['sources']['column'] = pd.DataFrame([
            {'column': 'country', 'text': 'These sources apply to countries.'},
            {'column': 'country', 'text': 'These apply to countries too.'},
        ])

        df.update(refs)
        refed_data, ref_list = generate_table_data(df,
                                                   column_names=[
                                                    'Country',
                                                    'HPV prevalence'
                                                    ])

        expected_data = df['data']
        expected_data.columns = ['Country$^{1,2}$', 'HPV prevalence']
        expected_reference_list = [
            ('1', 'These sources apply to countries.'),
            ('2', 'These apply to countries too.')
        ]
        pd.testing.assert_frame_equal(refed_data, expected_data)
        self.assertEqual(ref_list, expected_reference_list)

    def test_row_sources(self):
        df = {'data': self.data}
        refs = self.sample_refs

        refs['sources']['row'] = pd.DataFrame([
            {'row': 0, 'text': 'These sources apply to the first row.'},
            {'row': 0, 'text': 'These apply to the first row too.'},
        ])

        df.update(refs)
        refed_data, ref_list = generate_table_data(
                                    df,
                                    row_id_column='prevalence',
                                    column_names=['Country', 'HPV prevalence'])

        expected_data = df['data']
        val = expected_data.loc[0, 'prevalence']
        expected_data.loc[0, 'prevalence'] = "{}$^{{1,2}}$".format(val)
        expected_data.columns = ['Country', 'HPV prevalence']
        expected_reference_list = [
            ('1', 'These sources apply to the first row.'),
            ('2', 'These apply to the first row too.')
        ]
        pd.testing.assert_frame_equal(refed_data, expected_data)
        self.assertEqual(ref_list, expected_reference_list)

    def test_mixed(self):
        df = {'data': self.data}
        refs = self.sample_refs

        refs['sources']['row'] = pd.DataFrame([
            {'row': 0, 'text': 'These sources apply to the first row.'},
            {'row': 2, 'text': 'These apply to the third row.'},
        ])
        refs['methods']['global'] = pd.DataFrame([
            {'text': 'Method #1'},
        ])
        refs['notes']['row'] = pd.DataFrame([
            {'row': 2, 'text': 'This note applies to the third row.'},
        ])
        refs['years']['column'] = pd.DataFrame([
            {'column': 'country', 'text': '2010-2012'},
        ])

        df.update(refs)
        df['data']['row_header'] = [str(i)
                                    for i in range(len(df['data'].index))]
        df['data'] = df['data'][['row_header', 'country', 'prevalence']]

        refed_data, ref_list = generate_table_data(
                                df,
                                row_id_column='row_header',
                                column_names=['Row header',
                                              'Country',
                                              'HPV prevalence'])

        expected_data = df['data']
        val = expected_data.loc[0, 'row_header']
        expected_data.loc[0, 'row_header'] = "{}$^{{1}}$".format(val)

        val = expected_data.loc[2, 'row_header']
        expected_data.loc[2, 'row_header'] = "{}$^{{2,a}}$".format(val)

        expected_data.columns = [
            'Row header',
            'Country$^{\\Diamond}$',
            'HPV prevalence'
        ]
        expected_reference_list = [
            ('1', 'These sources apply to the first row.'),
            ('2', 'These apply to the third row.'),
            ('a', 'This note applies to the third row.'),
            ('\\alpha', 'Method #1'),
            ('\\Diamond', '2010-2012'),
        ]
        pd.testing.assert_frame_equal(refed_data, expected_data)
        self.assertEqual(ref_list, expected_reference_list)

    def test_cell_sources(self):
        df = {'data': self.data}
        refs = self.sample_refs

        refs['sources']['cell'] = pd.DataFrame([
            {
                'row': 0, 'column': 'prevalence',
                'text': 'These sources apply to this cell.'
            },
            {
                'row': 0, 'column': 'prevalence',
                'text': 'These apply to this cell too.'
            },
            {
                'row': 2, 'column': 'prevalence',
                'text': 'These apply to another cell.'
            },
            {
                'row': 1, 'column': 'country',
                'text': 'These apply to yet another cell.'
            },
        ])

        df.update(refs)
        refed_data, ref_list = generate_table_data(
                                    df,
                                    row_id_column='prevalence',
                                    column_names=['Country', 'HPV prevalence'])

        expected_data = df['data']

        val = expected_data.loc[0, 'prevalence']
        expected_data.loc[0, 'prevalence'] = "{}$^{{1,2}}$".format(val)

        val = expected_data.loc[1, 'country']
        expected_data.loc[1, 'country'] = "{}$^{{3}}$".format(val)

        val = expected_data.loc[2, 'prevalence']
        expected_data.loc[2, 'prevalence'] = "{}$^{{4}}$".format(val)

        expected_data.columns = ['Country', 'HPV prevalence']

        expected_reference_list = [
            ('1', 'These sources apply to this cell.'),
            ('2', 'These apply to this cell too.'),
            ('3', 'These apply to yet another cell.'),
            ('4', 'These apply to another cell.'),
        ]
        pd.testing.assert_frame_equal(refed_data, expected_data)
        self.assertEqual(ref_list, expected_reference_list)
