"""Step 4: Indic -> English translation with AI4Bharat IndicTrans2 (distilled 200M by default)."""
import os
import re

LANG_TAG = {"HI": "hin_Deva", "TE": "tel_Telu"}


def _load_indictrans_tokenizer(name):
    """Load the IndicTrans2 tokenizer as a *slow* tokenizer.

    transformers 5.x always builds a fast (`tokenizers`) backend, but the IndicTrans2
    remote tokenizer ships no `tokenizer.json`/`.model` — its vocab is split across
    `dict.SRC.json`/`dict.TGT.json` + `model.SRC`/`model.TGT`, which the fast converter
    does not understand. So we instantiate the slow `IndicTransTokenizer` class directly
    from the cached snapshot directory.
    """
    import importlib
    from transformers.utils.hub import cached_file
    from transformers.dynamic_module_utils import get_class_from_dynamic_module

    cls = get_class_from_dynamic_module(
        "tokenization_indictrans.IndicTransTokenizer", name, trust_remote_code=True
    )
    files = {fid: cached_file(name, fid, local_files_only=True) for fid in (
        "dict.SRC.json", "dict.TGT.json", "model.SRC", "model.TGT",
        "tokenizer_config.json",
    )}
    return cls(
        src_vocab_fp=files["dict.SRC.json"],
        tgt_vocab_fp=files["dict.TGT.json"],
        src_spm_fp=files["model.SRC"],
        tgt_spm_fp=files["model.TGT"],
    )


class IndicTrans2Translator:
    def __init__(self, model_name=None, device=None, beams=5, max_len=256):
        import torch
        try:
            from IndicTransToolkit import IndicProcessor
        except Exception:  # e.g. Windows without a C++ compiler: use the pure-Python stand-in
            from .indic_shim import IndicProcessor
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        name = model_name or os.getenv("MT_MODEL", "ai4bharat/indictrans2-indic-en-dist-200M")
        self.torch, self.beams, self.max_len = torch, beams, max_len
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        # use_fast=False: the IndicTrans2 remote tokenizer has no fast (tokenizers) backend
        # serialization, so TokenizerFast conversion fails on tokenizers 0.23+.
        # transformers 5.x forces a fast (tokenizers) backend for every tokenizer, but the
        # IndicTrans2 remote tokenizer has no tokenizer.json/.model that the fast converter
        # understands (its vocab is split across dict.SRC/dict.TGT + model.SRC/model.TGT).
        # Load the slow tokenizer class directly from the cached snapshot instead.
        self.tok = _load_indictrans_tokenizer(name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(name, trust_remote_code=True).to(self.device).eval()
        self.ip = IndicProcessor(inference=True)

    def translate(self, sentences, lang):
        """lang: 'HI' or 'TE' (source language of the whole batch)."""
        if not sentences:
            return []
        batch = self.ip.preprocess_batch(sentences, src_lang=LANG_TAG[lang], tgt_lang="eng_Latn")
        enc = self.tok(batch, truncation=True, padding="longest", return_tensors="pt",
                       return_attention_mask=True).to(self.device)
        with self.torch.no_grad():
            out = self.model.generate(**enc, use_cache=True, min_length=0,
                                      max_length=min(self.max_len, 2 * enc["input_ids"].shape[1] + 24), num_beams=self.beams, num_return_sequences=1)
        dec = self.tok.batch_decode(out, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        dec = [re.sub(r"(.)\1{5,}", r"\1\1\1", d) for d in dec]  # safeguard against runaway repetition ("ohhhhhh...")
        return self.ip.postprocess_batch(dec, lang="eng_Latn")
