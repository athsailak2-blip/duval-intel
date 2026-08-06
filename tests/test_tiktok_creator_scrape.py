import importlib.util
import os
import unittest
from argparse import Namespace
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location("tiktok_creator_scrape", "scripts/tiktok_creator_scrape.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TikTokKeywordSearchTests(unittest.TestCase):
    def test_keyword_search_paginates_and_deduplicates(self):
        pages = iter([
            {"search_item_list": [{"aweme_info": {"aweme_id": "1", "desc": "app launch"}}], "cursor": 2},
            {"search_item_list": [{"aweme_info": {"aweme_id": "1"}}, {"aweme_info": {"aweme_id": "2"}}], "cursor": 0},
        ])

        with patch.object(MODULE, "request_json", side_effect=lambda *args, **kwargs: next(pages)) as request:
            videos = MODULE.collect_keyword_videos(("app launch",), "US", 2, "secret-not-printed")

        self.assertEqual([video["aweme_id"] for video in videos], ["1", "2"])
        self.assertEqual([call.args[1]["cursor"] for call in request.call_args_list], ["", "2"])
        self.assertEqual(videos[0]["search_keyword"], "app launch")

    def test_collect_keyword_mode_skips_profile_request(self):
        args = Namespace(
            keyword=["app review"], user_id=None, region="US", max_candidates=1,
            transcripts=False, delay=0, term=["app"],
        )
        search_video = {
            "aweme_id": "42", "desc": "download this app",
            "author": {"unique_id": "creator"},
        }
        with patch.dict(os.environ, {"SCRAPECREATORS_API_KEY": "secret-not-printed"}), \
             patch.object(MODULE, "request_json", side_effect=[
                 {"search_item_list": [{"aweme_info": search_video}], "cursor": 0},
                 {"desc": "download this app"},
             ]) as request:
            result = MODULE.collect(args)

        self.assertEqual(result["keywords"], ["app review"])
        self.assertEqual(result["records"][0]["search_keyword"], "app review")
        self.assertEqual(request.call_args_list[0].args[0], "/v1/tiktok/search/keyword")


if __name__ == "__main__":
    unittest.main()
