# Model and dataset recovery instructions

All downloads are pinned; no command below launches scientific execution.
Authenticate interactively with the provider and never place credentials in a
script.

| Asset | Exact source/revision | Local verification |
|---|---|---|
| Qwen | `Qwen/Qwen3-1.7B-GGUF`, revision `90862c4b9d2787eaed51d12237eafdfe7c5f6077`, `Qwen3-1.7B-Q8_0.gguf` | SHA-256 `061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a`, 1,834,426,016 bytes |
| Gemma | `google/gemma-3-4b-it-qat-q4_0-gguf`, revision `15f73f5eee9c28f53afefef5723e29680c2fc78a`, `gemma-3-4b-it-q4_0.gguf` | SHA-256 `76aed0a8285b83102f18b5d60e53c70d09eb4e9917a20ce8956bd546452b56e2`, 3,155,051,328 bytes |
| Falcon | `tiiuae/Falcon-H1-7B-Instruct-GGUF`, revision `058c8c8f08e57da131ba5f070f9ff1280d141c39`, `Falcon-H1-7B-Instruct-Q4_K_M.gguf` | SHA-256 `145def0b4cd36500bf538ed7ac895b5c1851e02e802b2d1c12ffa6afdbaff25d`, 4,598,344,960 bytes |
| IndicTrans2 | `ai4bharat/indictrans2-indic-en-1B`, revision `ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a` | Verify artifact manifest `84cad691…`; primary `model.safetensors` SHA-256 `9b030cdd…` |
| Dataset | `large-traversaal/openbookqa_urdu_final`, revision `e4186f6ba5c3395c6f5cc99e1efadd7755ed4055` | Verify `engineering/workshop_v1_dataset_summary.json`; do not redistribute item text without license review |
| llama.cpp | source checkout commit `5266f24da75dc449bd56cbed7addb9c8e4a6a73e` | Rebuild and verify binary hash `1370ac1f…` |

Use the existing pinned bootstrap scripts and the local recovery manifests to
verify complete file lists. The dataset and model files are intentionally not
stored in Git.
