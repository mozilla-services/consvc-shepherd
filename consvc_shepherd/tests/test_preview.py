from unittest import mock

from django.test import TestCase, override_settings

from consvc_shepherd.preview import Environment, Spoc, Tile, get_ads


@override_settings(DEBUG=True)
class TestGetAds(TestCase):

    def mock_get_tiles(*args) -> list[Tile]:
        """Mock out either type of request for tiles within get_ads ('GET /v1/tiles' or 'POST /spocs for sponsored-topsites')"""
        print("mock get_tiles")
        return [
                Tile(
                    image_url="https://picsum.photos/48",
                    name="ACME",
                    sponsored="Sponsored",
                ),
                Tile(
                    image_url="https://picsum.photos/48",
                    name="Zombocom",
                    sponsored="Sponsored",
                )
            ]

    def mock_get_spocs(self, *args) -> list[Spoc]:
        """Mock out the POST /spocs requests within get_ads"""
        print("mock get_spocs")
        return [
            Spoc(
                image_src="https://picsum.photos/296/148",
                title="There is a Sale",
                domain="cosmetics.beauty",
                excerpt="The sale has begun..",
                sponsored_by="Sponsored by Cosmetics",
            ),

        ]

    def test_get_ads(self):
        """Test of the get_ads function that backs the preview page."""
        with mock.patch(
            "consvc_shepherd.preview.get_spocs", side_effect=self.mock_get_spocs
        ):
            with mock.patch(
                "consvc_shepherd.preview.get_tiles", side_effect=self.mock_get_tiles
            ):
                with mock.patch(
                    "consvc_shepherd.preview.get_direct_sold_tiles", side_effect=self.mock_get_tiles
                ):
                    mockEnv = Environment(
                        code="mock",
                        name="Mock",
                        mars_url="https://mars.mock.if.you.are.connecting.to.this.the.test.broke.com",
                        spoc_site_id=1234567,
                        direct_sold_tile_zone_id=424242)
                    ads = get_ads(mockEnv, "US", "CA")
                    print("ads")
                    print(ads)


# Test that expected get_*s are called based on env param unified or other
# Test that response are processed correctly in the Ads object
