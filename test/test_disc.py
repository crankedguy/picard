# -*- coding: utf-8 -*-
#
# Picard, the next-generation MusicBrainz tagger
#
# Copyright (C) 2020-2021 Philipp Wolfer
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


import unittest
from unittest.mock import (
    Mock,
    patch,
)

from test.picardtestcase import PicardTestCase

import picard.disc


class MockDisc:

    id = 'lSOVc5h6IXSuzcamJS1Gp4_tRuA-'
    mcn = '5029343070452'
    tracks = list(range(0, 11))
    toc_string = '1 11 242457 150 44942 61305 72755 96360 130485 147315 164275 190702 205412 220437'
    submission_url = 'https://musicbrainz.org:443/cdtoc/attach?id=lSOVc5h6IXSuzcamJS1Gp4_tRuA-&tracks=11&toc=1+11+242457+150+44942+61305+72755+96360+130485+147315+164275+190702+205412+220437'


class DiscTest(PicardTestCase):
    @unittest.skipUnless(picard.disc.discid, "discid not available")
    def test_raise_disc_error(self):
        disc = picard.disc.Disc()
        self.assertRaises(picard.disc.discid.DiscError, disc.read, 'notadevice')

    @patch.object(picard.disc, 'discid')
    def test_read(self, mock_discid):
        self.set_config_values(setting={
            'server_host': 'musicbrainz.org',
            'server_port': 443,
            'use_server_for_submission': False,
        })
        mock_discid.read = Mock(return_value=MockDisc())
        device = '/dev/cdrom1'
        disc = picard.disc.Disc()
        self.assertEqual(None, disc.id)
        self.assertEqual(None, disc.mcn)
        self.assertEqual(0, disc.tracks)
        self.assertEqual(None, disc.toc_string)
        self.assertEqual(None, disc.submission_url)
        disc.read(device)
        mock_discid.read.assert_called_with(device, features=['mcn'])
        self.assertEqual(MockDisc.id, disc.id)
        self.assertEqual(MockDisc.mcn, disc.mcn)
        self.assertEqual(11, disc.tracks)
        self.assertEqual(MockDisc.toc_string, disc.toc_string)
        self.assertEqual(MockDisc.submission_url, disc.submission_url)

    @patch.object(picard.disc, 'discid')
    def test_submission_url(self, mock_discid):
        self.set_config_values(setting={
            'server_host': 'test.musicbrainz.org',
            'server_port': 80,
            'use_server_for_submission': True,
        })
        mock_discid.read = Mock(return_value=MockDisc())
        disc = picard.disc.Disc()
        disc.read()
        self.assertEqual(
            'http://test.musicbrainz.org:80/cdtoc/attach?id=lSOVc5h6IXSuzcamJS1Gp4_tRuA-&tracks=11&toc=1+11+242457+150+44942+61305+72755+96360+130485+147315+164275+190702+205412+220437',
            disc.submission_url
        )
