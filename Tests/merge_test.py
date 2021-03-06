import sys
import unittest
import contextlib

import fontTools
from fontTools.misc.py23 import *
from fontTools import ttLib
from fontTools.merge import *
from fontTools.misc.loggingTools import CapturingLogHandler
from fontTools.ttLib.tables.otTables import GSUB, SingleSubst, LangSys, LookupList, Lookup, Feature, FeatureList, FeatureRecord, Script, ScriptList, ScriptRecord, LigatureSubst, Ligature


@contextlib.contextmanager
def mockIsGlyphSame(boolean):
	tmp = fontTools.merge.isGlyphSame
	fontTools.merge.isGlyphSame = lambda fonts, ogid, gid : boolean
	yield
	fontTools.merge.isGlyphSame = tmp


class MergeIntegrationTest(unittest.TestCase):
	# TODO
	pass
class GSUBMergUnitTest(unittest.TestCase):
	def buildGSUB(self):
		"""Constructs a basic GSUB table. Test cases can modify this table for their
			own usage.

			Return:
				{
					LookupList: {
						Lookup: [
							{
								LookupType: 4, # Ligature
								LookupFlag: 0,
								SubTable: [
									ligatures: {
										'f': {
											LigGlyph: 'f_i',
											Component: 'i',
											CompCount: 2,
										},
									},
									Format: 1,
									LookupType: 4, # Ligature
								],
								SubTableCount = 1,
							},
						],
						LookupCount = 1,
					},
					FeatureList: {
						FeatureRecord: [
							{
								FeatureTag: 'liga',
								Feature: {
									FeatureParams: None,
									LookupCount: 1,
									LookupListIndex: [0],
								},
							},
						],
						FeatureCount: 1,
					},
					ScriptList: {
						ScriptRecord: [
							{
								ScriptTag: 'tag1',
								Script: {
									DefaultLangSys: {
										LookupOrder: None,
										ReqFeatureIndex: 0xffff,
										FeatureIndex: [0],
										FeatureCount: 1,
									}
								}
							}
						],
						ScriptCount: 1,
					},
				}
		"""
		# Construct GSUB table bottom-up.
		li_fi = Ligature()
		li_fi.LigGlyph = 'f_i'
		li_fi.Component = ['i']
		li_fi.CompCount = 2

		liSubst = LigatureSubst()
		liSubst.ligatures = {'f': li_fi}
		liSubst.Format = 1
		liSubst.LookupType = 4

		lookup = Lookup()
		lookup.LookupType = 4 # Ligature
		lookup.LookupFlag = 0
		lookup.SubTable = [liSubst]
		lookup.SubTableCount = len(lookup.SubTable)

		lookupList = LookupList()
		lookupList.Lookup = [lookup]
		lookupList.LookupCount = len(lookupList.Lookup)

		fea = Feature()
		fea.FeatureParams = None
		fea.LookupCount = 1
		fea.LookupListIndex = [0]

		feaRecord = FeatureRecord()
		feaRecord.FeatureTag = 'liga'
		feaRecord.Feature = fea

		feaList = FeatureList()
		feaList.FeatureRecord = [feaRecord]
		feaList.FeatureCount = len(feaList.FeatureRecord)

		langSys = LangSys()
		langSys.LookupOrder = None
		langSys.ReqFeatureIndex = 0xFFFF
		langSys.FeatureIndex = [0]
		langSys.FeatureCount = len(langSys.FeatureIndex)

		sct = Script()
		sct.DefaultLangSys = langSys
		sct.LangSysRecord = []
		sct.LangSysCount = len(sct.LangSysRecord)

		sctRec = ScriptRecord()
		sctRec.ScriptTag = 'tag1'
		sctRec.Script = sct

		sctList = ScriptList()
		sctList.ScriptRecord = [sctRec]
		sctList.ScriptCount = len(sctList.ScriptRecord)

		gsub = GSUB()
		gsub.LookupList = lookupList
		gsub.FeatureList = feaList
		gsub.ScriptList = sctList

		table = ttLib.newTable('GSUB')
		table.table = gsub
		return table

	def preMerge(self, t):
		"""Map indices to references. This part is copied from ttLib.merge._preMerge
		"""
		if t.table.LookupList:
			lookupMap = {i:id(v) for i,v in enumerate(t.table.LookupList.Lookup)}
			t.table.LookupList.mapLookups(lookupMap)
			if t.table.FeatureList:
				# XXX Handle present FeatureList but absent LookupList
				t.table.FeatureList.mapLookups(lookupMap)

		if t.table.FeatureList and t.table.ScriptList:
			featureMap = {i:id(v) for i,v in enumerate(t.table.FeatureList.FeatureRecord)}
			t.table.ScriptList.mapFeatures(featureMap)

	def setUp(self):
		self.merger = Merger()

		self.table1 = self.buildGSUB()

		self.table2 = self.buildGSUB()
		self.table2.table.ScriptList.ScriptRecord[0].ScriptTag = 'tag2'
		self.table2.table.FeatureList.FeatureRecord[0].FeatureTag = 'aalt'
		self.table2.table.LookupList.Lookup[0].LookupType = 1 # single lookup type
		sub = SingleSubst()
		sub.SubstFormat = 1
		sub.DeltaGlyphID = 1024
		self.table2.table.LookupList.Lookup[0].SubTable[0] = sub

		self.mergedTable = ttLib.newTable('GSUB')

	def test_GSUB_merge_no_dups(self):
		self.merger.duplicateGlyphsPerFont = [{}, {}]

		self.mergedTable.merge(self.merger, [self.table1, self.table2])
		table = self.mergedTable.table

		# Checks ScriptList
		self.assertEqual(table.ScriptList.ScriptCount, 2)
		self.assertIn(self.table1.table.ScriptList.ScriptRecord[0], table.ScriptList.ScriptRecord)
		self.assertIn(self.table2.table.ScriptList.ScriptRecord[0], table.ScriptList.ScriptRecord)

		# Checks LookupList
		self.assertEqual(table.LookupList.LookupCount, 2)
		self.assertIn(self.table1.table.LookupList.Lookup[0], table.LookupList.Lookup)
		self.assertIn(self.table2.table.LookupList.Lookup[0], table.LookupList.Lookup)

		# Checks FeatureList
		self.assertEqual(table.FeatureList.FeatureCount, 2)
		self.assertIn(self.table1.table.FeatureList.FeatureRecord[0], table.FeatureList.FeatureRecord)
		self.assertIn(self.table2.table.FeatureList.FeatureRecord[0], table.FeatureList.FeatureRecord)

	def test_GSUB_merge_with_dups(self):
		self.merger.duplicateGlyphsPerFont = [{}, {'uni0032#0': 'uni0032#1'}]
		self.preMerge(self.table1)
		self.preMerge(self.table2)

		self.mergedTable.merge(self.merger, [self.table1, self.table2])
		table = self.mergedTable.table

		# Checks ScriptList
		self.assertEqual(table.ScriptList.ScriptCount, 2)
		self.assertIn(self.table1.table.ScriptList.ScriptRecord[0], table.ScriptList.ScriptRecord)
		self.assertIn(self.table2.table.ScriptList.ScriptRecord[0], table.ScriptList.ScriptRecord)

		# Checks LookupList
		self.assertEqual(table.LookupList.LookupCount, 3)
		self.assertIn(self.table1.table.LookupList.Lookup[0], table.LookupList.Lookup)
		self.assertIn(self.table2.table.LookupList.Lookup[0], table.LookupList.Lookup)
		self.assertEqual(table.LookupList.Lookup[-1].LookupFlag, 0)
		self.assertEqual(table.LookupList.Lookup[-1].LookupType, 1)
		self.assertEqual(table.LookupList.Lookup[-1].SubTableCount, 1)
		self.assertEqual(table.LookupList.Lookup[-1].SubTable[0].mapping, self.merger.duplicateGlyphsPerFont[1])

		# Checks FeatureList
		self.assertEqual(table.FeatureList.FeatureCount, 3)
		self.assertIn(self.table1.table.FeatureList.FeatureRecord[0], table.FeatureList.FeatureRecord)
		self.assertIn(self.table2.table.FeatureList.FeatureRecord[0], table.FeatureList.FeatureRecord)
		self.assertEqual(table.FeatureList.FeatureRecord[-1].FeatureTag, 'locl')

	def test_GSUB_merge_with_same_dups_and_no_second_GSUB(self):
		self.table2 = NotImplemented
		self.merger.duplicateGlyphsPerFont = [{}, {'uni0032#0': 'uni0032#1'}]
		self.merger.fonts = []
		with mockIsGlyphSame(True):
			self.mergedTable.merge(self.merger, [self.table1, self.table2])
		table = self.mergedTable.table
		self.assertEqual(table, self.table1.table)

	def test_GSUB_merge_with_different_dups_and_no_second_GSUB(self):
		self.table2 = NotImplemented
		self.merger.duplicateGlyphsPerFont = [{}, {'uni0032#0': 'uni0032#1'}]
		self.merger.fonts = []
		self.merger.fontfiles = ['font1', 'font2']
		with mockIsGlyphSame(False):
			with CapturingLogHandler(fontTools.merge.log, "WARNING") as captor:
				self.mergedTable.merge(self.merger, [self.table1, self.table2])

		table = self.mergedTable.table
		self.assertEqual(table, self.table1.table)
		self.assertTrue(len([r for r in captor.records if r.msg != '']) > 0)
class IsGlyphSame(unittest.TestCase):
		def setUp(self):
			# FIXME? This test requires at least one complete TTFont object including
			# glyf, hmtx and vmtx tables.
			# Importing 'data/TestTTF-Regular.ttx' file and adding 'hmtx', 'vmtx'
			# manually doesn't work since its glyf table isn't intact. Probably we
			# need to import a true Font file as our test case data source.
			pass

class gaspMergeUnitTest(unittest.TestCase):
	def setUp(self):
		self.merger = Merger()

		self.table1 = ttLib.newTable('gasp')
		self.table1.version = 1
		self.table1.gaspRange = {
			0x8: 0xA ,
			0x10: 0x5,
		}

		self.table2 = ttLib.newTable('gasp')
		self.table2.version = 1
		self.table2.gaspRange = {
			0x6: 0xB ,
			0xFF: 0x4,
		}

		self.result = ttLib.newTable('gasp')

	def test_gasp_merge_basic(self):
		result = self.result.merge(self.merger, [self.table1, self.table2])
		self.assertEqual(result, self.table1)

		result = self.result.merge(self.merger, [self.table2, self.table1])
		self.assertEqual(result, self.table2)

	def test_gasp_merge_notImplemented(self):
		result = self.result.merge(self.merger, [NotImplemented, self.table1])
		self.assertEqual(result, NotImplemented)

		result = self.result.merge(self.merger, [self.table1, NotImplemented])
		self.assertEqual(result, self.table1)


class CmapMergeUnitTest(unittest.TestCase):
	def setUp(self):
		self.merger = Merger()
		self.table1 = ttLib.newTable('cmap')
		self.table2 = ttLib.newTable('cmap')
		self.mergedTable = ttLib.newTable('cmap')
		pass

	def tearDown(self):
		pass

	def makeSubtable(self, format, platformID, platEncID, cmap):
		module = ttLib.getTableModule('cmap')
		subtable = module.cmap_classes[format](format)
		(subtable.platformID,
			subtable.platEncID,
			subtable.language,
			subtable.cmap) = (platformID, platEncID, 0, cmap)
		return subtable

	# 4-3-1 table merged with 12-3-10 table with no dupes with codepoints outside BMP
	def test_cmap_merge_no_dupes(self):
		table1 = self.table1
		table2 = self.table2
		mergedTable = self.mergedTable

		cmap1 = {0x2603: 'SNOWMAN'}
		table1.tables = [self.makeSubtable(4,3,1, cmap1)]

		cmap2 = {0x26C4: 'SNOWMAN WITHOUT SNOW'}
		cmap2Extended = {0x1F93C: 'WRESTLERS'}
		cmap2Extended.update(cmap2)
		table2.tables = [self.makeSubtable(4,3,1, cmap2), self.makeSubtable(12,3,10, cmap2Extended)]

		self.merger.alternateGlyphsPerFont = [{},{}]
		mergedTable.merge(self.merger, [table1, table2])

		expectedCmap = cmap2.copy()
		expectedCmap.update(cmap1)
		expectedCmapExtended = cmap2Extended.copy()
		expectedCmapExtended.update(cmap1)
		self.assertEqual(mergedTable.numSubTables, 2)
		self.assertEqual([(table.format, table.platformID, table.platEncID, table.language) for table in mergedTable.tables],
			[(4,3,1,0),(12,3,10,0)])
		self.assertEqual(mergedTable.tables[0].cmap, expectedCmap)
		self.assertEqual(mergedTable.tables[1].cmap, expectedCmapExtended)

	# Tests Issue #322
	def test_cmap_merge_three_dupes(self):
		table1 = self.table1
		table2 = self.table2
		mergedTable = self.mergedTable

		cmap1 = {0x20: 'space#0', 0xA0: 'space#0'}
		table1.tables = [self.makeSubtable(4,3,1,cmap1)]
		cmap2 = {0x20: 'space#1', 0xA0: 'uni00A0#1'}
		table2.tables = [self.makeSubtable(4,3,1,cmap2)]

		self.merger.duplicateGlyphsPerFont = [{},{}]
		mergedTable.merge(self.merger, [table1, table2])

		expectedCmap = cmap1.copy()
		self.assertEqual(mergedTable.numSubTables, 1)
		table = mergedTable.tables[0]
		self.assertEqual((table.format, table.platformID, table.platEncID, table.language), (4,3,1,0))
		self.assertEqual(table.cmap, expectedCmap)
		self.assertEqual(self.merger.duplicateGlyphsPerFont, [{}, {'space#0': 'space#1'}])


if __name__ == "__main__":
	import sys
	sys.exit(unittest.main())
