# X-Brace Offset Feature Implementation Plan

X-Braceの主桁側接続点にオフセットを追加し、主桁側の幅を広げる（または狭める）機能を実装します。

## Proposed Changes

### `ui/batch_mode.py`
- **UI追加**: X-Brace Zones設定行に、それぞれのゾーンの「Offset (mm)」を入力できるエントリーを追加します。
- **パラメータ抽出**: `xb_zones` のタプルを `(start, end)` から `(start, end, offset)` の3要素に変更し、`core/engine.py` 側にオフセット値を渡します。

### `core/engine.py`
- **引数変更**: `RibParameters` の `local_xb_pct` を廃止し、新たに `xb_t_list: List[float]` を受け取るように変更します。
- **穴位置の計算ロジック変更**: 
  各リブのY座標（`y_global`）において、2本のワイヤー（たすき掛けの線）それぞれがメインスパー〜リアスパー間のどの割合（`t`）を通過するかを正確に計算します。
  - ワイヤー1: Main Spar `y_s - offset` 〜 Rear Spar `y_e`
  - ワイヤー2: Main Spar `y_e + offset` 〜 Rear Spar `y_s`
  計算した `t` （0.0〜1.0）を用いて、リブ上の穴の座標を `P_main_surf + u * (len_L * t)` として求めます。
  これにより、オフセットによってX-Braceが長くなり、ゾーン外のリブを貫通する場合でも正確に穴が開きます。

### `core/export_3d.py`
- **3Dメッシュ生成ロジック変更**: `_generate_xbrace_meshes` において、`xb_zones` から `offset` を受け取り、メインスパー側の接続点座標を以下のように変更します。
  - `p_main_s = np.array([0.0, y_m_s - offset, 0.0])`
  - `p_main_e = np.array([0.0, y_m_e + offset, 0.0])`
- **V字コネクタ等への巻き付け**: 上記で求めたベクトル `vec_s`, `vec_e` を用いて、正しく巻き付けポイントやワイヤーパイプメッシュが生成されるように調整します。

## Verification Plan
- `app.py` からUIを起動し、Offsetに正の数（例: 20mm）を入力してプレビューを確認する。
- 3Dモデル（glb）を出力し、主桁側のX-Braceが指定したオフセット分だけ外側に広がっていることを確認する。
- X-Braceが通るリブの穴が、ワイヤーの軌道と完全に一致していることを確認する。
