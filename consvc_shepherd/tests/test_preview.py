"""Unit tests for the preview page functionalities"""

from unittest import mock

from django.test import TestCase, override_settings

from consvc_shepherd.preview import (
    DIRECT_SOLD_TILE_AD_TYPES,
    LOCALIZATIONS,
    SPOC_AD_TYPES,
    Environment,
    FormFactor,
    Spoc,
    Tile,
    get_ads,
    get_amp_tiles,
    get_spocs_and_direct_sold_tiles,
    get_unified,
)

SPOC = Spoc(
    image_src="https://picsum.photos/296/148",
    title="There is a Sale",
    domain="cosmetics.beauty",
    excerpt="The sale has begun...",
    sponsored_by="Sponsored by Cosmetics",
    sponsor="Cosmetics",
    url="example.com",
)

ACME_TILE = Tile(
    image_url="https://picsum.photos/id/200/48/48",
    name="ACME",
    sponsored="Sponsored",
    url="example2.com",
)

ZOMBOCOM_TILE = Tile(
    image_url="https://picsum.photos/id/237/48/48",
    name="Zombocom",
    sponsored="Sponsored",
    url="example3.com",
)

PROGRESS_QUEST_TILE = Tile(
    image_url="https://picsum.photos/id/40/48/48",
    name="Progress Quest",
    sponsored="Sponsored",
    url="example4.com",
)

DEFAULT_USER_AGENT = FormFactor(
    code="desktop",
    name="Desktop",
    is_mobile=False,
    user_agent="Mozilla/5.0 (Windows NT 10.0; rv:10.0) Gecko/20100101 Firefox/91.0",
)


@override_settings(DEBUG=True)
class TestGetAmpTiles(TestCase):
    """Test the Fetching of Tiles for the Preview Page."""

    def mock_amp_tiles_data(self, *args, **kwargs):
        """Mock out the function that wraps 'GET /v1/tiles' request within get_amp_tiles"""
        response = {
            "tiles": [
                {
                    "id": 12345,
                    "name": "Example Tile",
                    "url": "https://www.example.com/?tag=example-tag",
                    "click_url": ("https://www.example.com/click?version=1.0.0"),
                    "image_url": (
                        "https://example-cdn.com/" "example-image-id=example.jpg"
                    ),
                    "impression_url": (
                        "https://example-impression-url.com/static?id="
                        "example-impression-id"
                    ),
                    "image_size": 300,
                }
            ]
        }
        return mock.Mock(status_code=200, json=lambda: response)

    def test_get_amp_tiles(self):
        """Test the Retrieval of Tiles from MARS."""
        with mock.patch(
            "requests.get",
            side_effect=self.mock_amp_tiles_data,
        ) as mock_amp_tiles:
            mockEnv = Environment(
                code="mock",
                name="Mock",
                mars_url="https://mars.mock.if.you.are.connecting.to.this.the.test.broke.com",
                spoc_site_id=1234567,
                spoc_site_id_mobile=1234567,
                spoc_zone_ids=[],
                direct_sold_tile_zone_ids=[424242],
            )
            mockFormFactor = FormFactor(
                code="desktop",
                name="Desktop",
                is_mobile=False,
                user_agent="Mozilla/5.0 (Windows NT 10.0; rv:10.0) Gecko/20100101 Firefox/91.0",
            )

            tiles = get_amp_tiles(mockEnv, "US", "CA", mockFormFactor.user_agent)

            mock_amp_tiles.assert_called()

            self.assertEqual(len(tiles), 1)
            self.assertEqual(
                tiles[0].image_url,
                "https://example-cdn.com/example-image-id=example.jpg",
            )

            self.assertEqual(tiles[0].name, "Example Tile")
            self.assertEqual(tiles[0].url, "https://www.example.com/?tag=example-tag")
            self.assertEqual(tiles[0].sponsored, LOCALIZATIONS["Sponsored"]["US"])

            # Verify that requests.get was called once with the expected parameters
            mock_amp_tiles.assert_called_once_with(
                f"{mockEnv.mars_url}/v1/tiles",
                params={"country": "US", "region": "CA"},
                headers={"User-Agent": mockFormFactor.user_agent},
                timeout=30,
            )


@override_settings(DEBUG=True)
class TestGetSpocsAndDirectSoldTiles(TestCase):
    """Test the Fetching of SPOCs and direct sold tiles for the Preview Page."""

    def mock_spocs_data(self, *args, **kwargs):
        """Mock out the function that wraps 'POST /spocs' request within get_spocs_and_direct_sold_tiles"""
        response = {
            "sponsored-topsite": [
                {
                    "raw_image_src": "image_src_1",
                    "title": "Topsite Tile 1",
                    "url": "https://example.com/tile1",
                },
            ],
            "spocs": [
                {
                    "image_src": "spoc_image_src_1",
                    "title": "Spoc 1",
                    "domain": "example.com",
                    "excerpt": "An example spoc.",
                    "url": "https://example.com/spoc1",
                    "sponsor": "Sponsor 1",
                },
            ],
        }
        return mock.Mock(status_code=200, json=lambda: response)

    def test_get_spocs_and_direct_sold_tiles(self):
        """Test the fetching of SPOCs and direct sold tiles from MARS."""
        mockEnv = Environment(
            code="mock",
            name="Mock",
            mars_url="https://mars.mock.if.you.are.connecting.to.this.the.test.broke.com",
            spoc_site_id=1234567,
            spoc_site_id_mobile=1234567,
            spoc_zone_ids=[111111],
            direct_sold_tile_zone_ids=[424242],
        )

        self._test_get_spocs_and_direct_sold_tiles_case(
            mockEnv, "US", "CA", False, mockEnv.spoc_site_id
        )

        self._test_get_spocs_and_direct_sold_tiles_case(
            mockEnv, "US", "CA", True, mockEnv.spoc_site_id_mobile
        )

    def _test_get_spocs_and_direct_sold_tiles_case(
        self,
        mockEnv: Environment,
        country: str,
        region: str,
        is_mobile: bool,
        expected_site_id: int | None,
    ):
        with mock.patch(
            "requests.post",
            side_effect=self.mock_spocs_data,
        ) as mock_spocs:
            tiles, spocs = get_spocs_and_direct_sold_tiles(
                mockEnv, country, region, is_mobile
            )

            mock_spocs.assert_called()

            self.assertEqual(len(tiles), 1)
            self.assertEqual(len(spocs), 1)

            # Check the properties of the tile
            self.assertIsNotNone(tiles[0].image_url)
            self.assertEqual(tiles[0].name, "Topsite Tile 1")
            self.assertEqual(tiles[0].url, "https://example.com/tile1")
            self.assertEqual(tiles[0].sponsored, LOCALIZATIONS["Sponsored"][country])

            # Check the properties of the spoc
            self.assertEqual(spocs[0].image_src, "spoc_image_src_1")
            self.assertEqual(spocs[0].title, "Spoc 1")
            self.assertEqual(spocs[0].domain, "example.com")
            self.assertEqual(spocs[0].excerpt, "An example spoc.")
            self.assertEqual(spocs[0].url, "https://example.com/spoc1")
            self.assertEqual(spocs[0].sponsor, "Sponsor 1")
            if is_mobile:
                self.assertEqual(spocs[0].sponsored_by, "Sponsored")
            else:
                self.assertEqual(spocs[0].sponsored_by, "Sponsored by Sponsor 1")

            # Ensure requests.post was called with the correct URL and payload
            mock_spocs.assert_called_once_with(
                f"{mockEnv.mars_url}/spocs",
                json={
                    "pocket_id": mock.ANY,  # Use mock.ANY to match any UUID
                    "site": expected_site_id,
                    "version": 2,
                    "country": country,
                    "region": region,
                    "placements": [
                        {
                            "name": "sponsored-topsite",
                            "zone_ids": mockEnv.direct_sold_tile_zone_ids,
                            "ad_types": DIRECT_SOLD_TILE_AD_TYPES,
                        },
                        {
                            "name": "spocs",
                            "zone_ids": mockEnv.spoc_zone_ids,
                            "ad_types": SPOC_AD_TYPES,
                        },
                    ],
                },
                timeout=30,
            )

            args, kwargs = mock_spocs.call_args
            payload = kwargs["json"]
            self.assertIsInstance(payload["pocket_id"], str)
            self.assertEqual(len(payload["pocket_id"]), 38)


@override_settings(DEBUG=True)
class TestGetAds(TestCase):
    """Test the fetching of various ads on the preview page"""

    def mock_get_amp_tiles(self, *args) -> list[Tile]:
        """Mock out the function that wraps 'GET /v1/tiles' request within get_ads"""
        return [ACME_TILE, ZOMBOCOM_TILE]

    def mock_get_spocs_and_direct_sold_tiles(
        self, *args
    ) -> tuple[list[Tile], list[Spoc]]:
        """Mock out the POST /spocs requests within get_ads"""
        return ([PROGRESS_QUEST_TILE], [SPOC])

    def test_get_ads(self):
        """Test of the get_ads function that backs the preview page."""
        with mock.patch(
            "consvc_shepherd.preview.get_spocs_and_direct_sold_tiles",
            side_effect=self.mock_get_spocs_and_direct_sold_tiles,
        ) as mock_get_spocs_and_direct_sold_tiles:
            with mock.patch(
                "consvc_shepherd.preview.get_amp_tiles",
                side_effect=self.mock_get_amp_tiles,
            ) as mock_get_amp_tiles:
                mockEnv = Environment(
                    code="mock",
                    name="Mock",
                    mars_url="https://mars.mock.if.you.are.connecting.to.this.the.test.broke.com",
                    spoc_site_id=1234567,
                    spoc_site_id_mobile=1234567,
                    spoc_zone_ids=[],
                    direct_sold_tile_zone_ids=[424242],
                )

                ads = get_ads(mockEnv, "US", "CA", DEFAULT_USER_AGENT)

                # Function calls
                mock_get_amp_tiles.assert_called_once_with(
                    mockEnv, "US", "CA", DEFAULT_USER_AGENT.user_agent
                )
                mock_get_spocs_and_direct_sold_tiles.assert_called_once_with(
                    mockEnv, "US", "CA", DEFAULT_USER_AGENT.is_mobile
                )
                self.assertEqual(len(ads.spocs), 1)
                self.assertEqual(len(ads.tiles), 3)

                # Spoc data
                self.assertEqual(ads.spocs[0].image_src, SPOC.image_src)
                self.assertEqual(ads.spocs[0].title, SPOC.title)
                self.assertEqual(ads.spocs[0].domain, SPOC.domain)
                self.assertEqual(ads.spocs[0].excerpt, SPOC.excerpt)
                self.assertEqual(ads.spocs[0].sponsored_by, SPOC.sponsored_by)
                self.assertEqual(ads.spocs[0].sponsor, SPOC.sponsor)
                self.assertEqual(ads.spocs[0].url, SPOC.url)

                # Tile data
                self.assertEqual(
                    ads.tiles[2].image_url, "https://picsum.photos/id/40/48/48"
                )
                self.assertEqual(ads.tiles[2].name, "Progress Quest")
                self.assertEqual(ads.tiles[2].sponsored, "Sponsored")
                self.assertEqual(ads.tiles[2].url, "example4.com")

    def test_get_ads_unified_env(self):
        """Test that when unified API environments are requested, the expected request wrapper functions are called"""
        with mock.patch("consvc_shepherd.preview.get_unified") as mock_get_unified:
            mockUnifiedEnv = Environment(
                code="unified_mock",
                name="Unified Mock",
                mars_url="https://unified.mock.if.you.are.connecting.to.this.the.test.broke.com",
                spoc_site_id=1234567,
                spoc_site_id_mobile=1234567,
                spoc_zone_ids=[1010101],
                direct_sold_tile_zone_ids=[424242],
            )
            get_ads(mockUnifiedEnv, "US", "CA", DEFAULT_USER_AGENT)

            mock_get_unified.assert_called_once_with(
                mockUnifiedEnv, "US", DEFAULT_USER_AGENT.is_mobile
            )


@override_settings(DEBUG=True)
class TestGetUnified(TestCase):
    """Test the Retrieval of Ads from MARS Unified API."""

    def mock_unified_data(self, *args, **kwargs):
        """Mock out the function that wraps 'POST /v1/ads' request within get_unified"""
        response = {
            "newtab_spocs": [
                {
                    "image_url": "https://example-spoc-cdn.com/spoc-image.jpg",
                    "title": "Example Spoc",
                    "domain": "example.com",
                    "excerpt": "An example spoc.",
                    "url": "https://example.com/spoc",
                    "sponsor": "Sponsor 1",
                }
            ],
            "newtab_tile_1": [
                {
                    "image_url": "https://example-tile-cdn.com/tile1.jpg",
                    "name": "Tile 1",
                    "url": "https://example.com/tile1",
                }
            ],
            "newtab_tile_2": [
                {
                    "image_url": "https://example-tile-cdn.com/tile2.jpg",
                    "name": "Tile 2",
                    "url": "https://example.com/tile2",
                }
            ],
            "newtab_tile_3": [
                {
                    "image_url": "https://example-tile-cdn.com/tile3.jpg",
                    "name": "Tile 3",
                    "url": "https://example.com/tile3",
                }
            ],
        }
        return mock.Mock(status_code=200, json=lambda: response)

    def test_get_unified(self):
        """Test the Retrieval of Ads from MARS Unified API."""
        with mock.patch(
            "requests.post",
            side_effect=self.mock_unified_data,
        ) as mock_unified:
            mockUnifiedEnv = Environment(
                code="unified_mock",
                name="Unified Mock",
                mars_url="https://unified.mock.if.you.are.connecting.to.this.the.test.broke.com",
                spoc_site_id=1234567,
                spoc_site_id_mobile=1234567,
                spoc_zone_ids=[1010101],
                direct_sold_tile_zone_ids=[424242],
            )

            ads = get_unified(mockUnifiedEnv, "US", is_mobile=False)

            mock_unified.assert_called()

            # Verify the tiles
            self.assertEqual(len(ads.tiles), 3)
            self.assertEqual(
                ads.tiles[0].image_url, "https://example-tile-cdn.com/tile1.jpg"
            )
            self.assertEqual(ads.tiles[0].name, "Tile 1")
            self.assertEqual(ads.tiles[0].url, "https://example.com/tile1")
            self.assertEqual(
                ads.tiles[1].image_url, "https://example-tile-cdn.com/tile2.jpg"
            )
            self.assertEqual(ads.tiles[1].name, "Tile 2")
            self.assertEqual(ads.tiles[1].url, "https://example.com/tile2")
            self.assertEqual(
                ads.tiles[2].image_url, "https://example-tile-cdn.com/tile3.jpg"
            )
            self.assertEqual(ads.tiles[2].name, "Tile 3")
            self.assertEqual(ads.tiles[2].url, "https://example.com/tile3")

            # Verify the spocs
            self.assertEqual(len(ads.spocs), 1)
            self.assertEqual(
                ads.spocs[0].image_src, "https://example-spoc-cdn.com/spoc-image.jpg"
            )
            self.assertEqual(ads.spocs[0].title, "Example Spoc")
            self.assertEqual(ads.spocs[0].domain, "example.com")
            self.assertEqual(ads.spocs[0].excerpt, "An example spoc.")
            self.assertEqual(ads.spocs[0].url, "https://example.com/spoc")
            self.assertEqual(ads.spocs[0].sponsor, "Sponsor 1")
            self.assertEqual(ads.spocs[0].sponsored_by, "Sponsored by Sponsor 1")

            # Verify the is_mobile
            self.assertFalse(ads.is_mobile)

            # Verify that requests.post was called once with the expected parameters
            mock_unified.assert_called_once_with(
                f"{mockUnifiedEnv.mars_url}/v1/ads",
                json={
                    "context_id": mock.ANY,
                    "placements": [
                        {"placement": "newtab_spocs", "count": 10},
                        {"placement": "newtab_tile_1", "count": 1},
                        {"placement": "newtab_tile_2", "count": 1},
                        {"placement": "newtab_tile_3", "count": 1},
                    ],
                },
                timeout=30,
            )

            args, kwargs = mock_unified.call_args
            payload = kwargs["json"]
            self.assertIsInstance(payload["context_id"], str)
            self.assertEqual(len(payload["context_id"]), 36)
