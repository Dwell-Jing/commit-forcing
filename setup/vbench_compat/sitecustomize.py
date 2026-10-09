"""Import fixes that let VBench 45e79ec run with setup/requirements.txt; no computation changes.

peft 0.19 with torchao 0.15 (DreamSim), numpy 2 without numpy.lib.function_base (UMT), transformers 4.57 with three
helpers moved to pytorch_utils (Tag2Text)."""
try:
    import peft.import_utils as _piu
    _piu.is_torchao_available = lambda: False
    import peft.tuners.lora.torchao as _plt
    _plt.is_torchao_available = lambda: False
except Exception:
    pass

try:
    import numpy.lib.function_base  # noqa: F401
except Exception:
    import sys as _sys
    import types as _types
    _fb = _types.ModuleType("numpy.lib.function_base")
    _fb.disp = lambda mesg, device=None, linefeed=True: print(mesg, end="\n" if linefeed else "")
    _sys.modules["numpy.lib.function_base"] = _fb

try:
    import transformers.modeling_utils as _tmu
    import transformers.pytorch_utils as _tpu
    for _n in ("apply_chunking_to_forward", "find_pruneable_heads_and_indices", "prune_linear_layer"):
        if not hasattr(_tmu, _n) and hasattr(_tpu, _n):
            setattr(_tmu, _n, getattr(_tpu, _n))
except Exception:
    pass
