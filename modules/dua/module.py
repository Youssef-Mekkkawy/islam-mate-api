from fastapi import APIRouter, Query, HTTPException, Request
import json
import os
import random

from base.base_module import BaseModule

HF_BASE   = "https://huggingface.co/datasets/elprofessorai/islam-mate-data/resolve/main"
DATA_FILE = "data/dua/metadata.json"


class Module(BaseModule):
    name         = "dua"
    version      = "1.0.0"
    dependencies = []

    def __init__(self, service_container):
        super().__init__(service_container)
        self._categories = None   # list, cached on first request

    # ── Route registration ────────────────────────────────────────────────────

    def register_routes(self, router: APIRouter):
        router.add_api_route("/dua/categories",          self.get_categories,  methods=["GET"])
        router.add_api_route("/dua/category/{id}",       self.get_category,    methods=["GET"])
        router.add_api_route("/dua/search",              self.search,          methods=["GET"])
        router.add_api_route("/dua/random",              self.get_random,      methods=["GET"])

    # ── Data loading ──────────────────────────────────────────────────────────

    def _load(self) -> list:
        if self._categories is not None:
            return self._categories
        if not os.path.exists(DATA_FILE):
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Dua data not found locally.",
                    "hint": f"Run dua_pipeline.ipynb and place metadata.json at {DATA_FILE}"
                }
            )
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            self._categories = json.load(f)
        return self._categories

    # ── Formatters ────────────────────────────────────────────────────────────

    def _format_category(self, cat: dict, lang: str, include_duas: bool = False) -> dict:
        result = {
            "id"                 : cat["id"],
            "title"              : cat["title_ar"] if lang == "ar" else cat["title_en"],
            "title_ar"           : cat["title_ar"],
            "title_en"           : cat["title_en"],
            "count"              : len(cat.get("duas", [])),
            "category_audio_url" : cat.get("category_audio_hf_url") or None,
        }
        if include_duas:
            result["duas"] = [self._format_dua(d, lang) for d in cat.get("duas", [])]
        return result

    def _format_dua(self, dua: dict, lang: str) -> dict:
        return {
            "id"             : dua["id"],
            "arabic_text"    : dua.get("arabic_text", ""),
            "transliteration": dua.get("transliteration", ""),
            "translation"    : dua.get("translation", "") if lang == "en" else "",
            "repeat"         : dua.get("repeat", 1),
            "audio_url"      : dua.get("audio_url") or None,
        }

    # ── Endpoints ─────────────────────────────────────────────────────────────

    async def get_categories(
        self,
        request : Request,
        lang    : str = Query("en", description="Language: en or ar"),
    ):
        """List all 132 dua categories."""
        lang       = self.get_lang(request, lang)
        categories = self._load()
        return {
            "total"     : len(categories),
            "categories": [self._format_category(c, lang) for c in categories],
        }

    async def get_category(
        self,
        id      : int,
        request : Request,
        lang    : str = Query("en", description="Language: en or ar"),
    ):
        """Get a single category with all its duas."""
        lang       = self.get_lang(request, lang)
        categories = self._load()
        cat = next((c for c in categories if c["id"] == id), None)
        if not cat:
            raise HTTPException(status_code=404, detail=f"Category {id} not found.")
        return self._format_category(cat, lang, include_duas=True)

    async def search(
        self,
        request : Request,
        q       : str = Query(..., min_length=1, description="Search by category title (AR or EN)"),
        lang    : str = Query("en", description="Language: en or ar"),
    ):
        """Search categories by title."""
        lang       = self.get_lang(request, lang)
        categories = self._load()
        q_low      = q.lower()
        matches    = [
            c for c in categories
            if q_low in c.get("title_en", "").lower() or q in c.get("title_ar", "")
        ]
        return {
            "query"     : q,
            "total"     : len(matches),
            "categories": [self._format_category(c, lang) for c in matches],
        }

    async def get_random(
        self,
        request : Request,
        lang    : str = Query("en", description="Language: en or ar"),
    ):
        """Return a random dua from a random category."""
        lang       = self.get_lang(request, lang)
        categories = self._load()

        candidates = [c for c in categories if c.get("duas")]
        if not candidates:
            raise HTTPException(status_code=503, detail="No dua data available.")

        cat = random.choice(candidates)
        dua = random.choice(cat["duas"])
        return {
            "category_id"  : cat["id"],
            "category_title": cat["title_ar"] if lang == "ar" else cat["title_en"],
            "dua"          : self._format_dua(dua, lang),
        }