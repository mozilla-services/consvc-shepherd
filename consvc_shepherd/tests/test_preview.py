from unittest import mock

from django.test import TestCase, override_settings

from consvc_shepherd.preview import Environment, Spoc, Tile, get_ads

SPOC: Spoc = Spoc(
    image_src="https://picsum.photos/296/148",
    title="There is a Sale",
    domain="cosmetics.beauty",
    excerpt="The sale has begun...",
    sponsored_by="Sponsored by Cosmetics",
)

ACME_TILE: Tile = Tile(
    image_url="https://picsum.photos/id/200/48/48",
    name="ACME",
    sponsored="Sponsored",
)

ZOMBOCOM_TILE: Tile = Tile(
    image_url="https://picsum.photos/id/237/48/48",
    name="Zombocom",
    sponsored="Sponsored",
)

PROGRESS_QUEST_TILE: Tile = Tile(
    image_url="https://picsum.photos/id/40/48/48",
    name="Progress Quest",
    sponsored="Sponsored",
)


@override_settings(DEBUG=True)
class TestGetAds(TestCase):

    def mock_get_tiles(self, *args) -> list[Tile]:
        """Mock out the function that wraps 'GET /v1/tiles' request within get_ads"""
        return [ACME_TILE, ZOMBOCOM_TILE]

    def mock_get_direct_sold_tiles(self, *args) -> list[Tile]:
        """Mock out the function that wraps 'POST /spocs' request for 'sponsored-topsites'"""
        return [PROGRESS_QUEST_TILE]

    def mock_get_spocs(self, *args) -> list[Spoc]:
        """Mock out the POST /spocs requests within get_ads"""
        return [SPOC]

    def test_get_ads(self):
        """Test of the get_ads function that backs the preview page."""
        with mock.patch(
            "consvc_shepherd.preview.get_spocs", side_effect=self.mock_get_spocs
        ) as mock_get_spocs:
            with mock.patch(
                "consvc_shepherd.preview.get_tiles", side_effect=self.mock_get_tiles
            ) as mock_get_tiles:
                with mock.patch(
                    "consvc_shepherd.preview.get_direct_sold_tiles",
                    side_effect=self.mock_get_direct_sold_tiles,
                ) as mock_get_direct_sold_tiles:
                    mockEnv = Environment(
                        code="mock",
                        name="Mock",
                        mars_url="https://mars.mock.if.you.are.connecting.to.this.the.test.broke.com",
                        spoc_site_id=1234567,
                        direct_sold_tile_zone_id=424242,
                    )
                    ads = get_ads(mockEnv, "US", "CA")

                    # Function calls
                    mock_get_spocs.assert_called_once_with(mockEnv, "US", "CA")
                    mock_get_tiles.assert_called_once_with(mockEnv, "US", "CA")
                    mock_get_direct_sold_tiles.assert_called_once_with(
                        mockEnv, "US", "CA"
                    )
                    self.assertEqual(len(ads.spocs), 1)
                    self.assertEqual(len(ads.tiles), 3)

                    # Spoc data
                    self.assertEqual(ads.spocs[0].image_src, SPOC.image_src)
                    self.assertEqual(ads.spocs[0].title, SPOC.title)
                    self.assertEqual(ads.spocs[0].domain, SPOC.domain)
                    self.assertEqual(ads.spocs[0].excerpt, SPOC.excerpt)
                    self.assertEqual(ads.spocs[0].sponsored_by, SPOC.sponsored_by)

                    # Tile data
                    self.assertEqual(
                        ads.tiles[2].image_url, "https://picsum.photos/id/40/48/48"
                    )
                    self.assertEqual(ads.tiles[2].name, "Progress Quest")
                    self.assertEqual(ads.tiles[2].sponsored, "Sponsored")

    def test_get_ads_unified_env(self):
        """Test that when unified API environments are requested, the expected request wrapper functions are called"""
        with mock.patch("consvc_shepherd.preview.get_unified") as mock_get_unified:
            mockUnifiedEnv = Environment(
                code="unified_mock",
                name="Unified Mock",
                mars_url="https://unified.mock.if.you.are.connecting.to.this.the.test.broke.com",
                spoc_site_id=1234567,
                direct_sold_tile_zone_id=424242,
            )
            ads = get_ads(mockUnifiedEnv, "US", "CA")

            mock_get_unified.assert_called_once_with(mockUnifiedEnv, "US")
