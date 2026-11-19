"""Public dashboard renderer with an explicit sensitive-data allowlist."""

from __future__ import annotations

import datetime
from typing import Any, Iterable


PUBLIC_STATE_KEYS = {
    "status",
    "detail",
    "rest_connected",
    "websocket_connected",
    "last_quote_at",
    "last_candle_at",
    "last_account_sync",
    "last_loop_at",
    "running_commit",
    "kill_switch",
    "drawdown_pct",
    "total_exposure_pct",
    "markets",
}

PUBLIC_MARKET_KEYS = {
    "market",
    "price",
    "change_24h_pct",
    "daily_trend",
    "four_hour_breakout",
    "signal",
    "blocker",
    "position_open",
    "position_exposure_pct",
    "return_pct",
    "stop_distance_pct",
}


def public_state(state: dict[str, Any]) -> dict[str, Any]:
    """Copy only fields that are safe for a public GitHub branch."""
    result = {key: state[key] for key in PUBLIC_STATE_KEYS if key in state}
    result["markets"] = [
        {key: market[key] for key in PUBLIC_MARKET_KEYS if key in market}
        for market in state.get("markets", [])
    ]
    return result


def _value(value: Any, default: str = "-") -> str:
    return default if value is None or value == "" else str(value)


def render_dashboard(
    state: dict[str, Any],
    events: Iterable[dict[str, Any]] = (),
    now: datetime.datetime | None = None,
) -> str:
    safe = public_state(state)
    now = now or datetime.datetime.now()
    status = safe.get("status", "starting")
    status_label = {
        "running": "🟢 정상",
        "halted": "🔴 거래 중단",
        "error": "🔴 오류",
        "starting": "🟡 준비 중",
    }.get(status, f"🟡 {_value(status)}")
    lines = [
        "# Quant Crypto Sniper Dashboard",
        "",
        f"> 마지막 갱신: **{now.strftime('%Y-%m-%d %H:%M:%S')} KST**",
        "",
        "## 실시간 상태",
        "",
        "| 시스템 | 상세 | REST | WebSocket | 킬스위치 |",
        "|---|---|---|---|---|",
        f"| {status_label} | {_value(safe.get('detail'))} "
        f"| {'정상' if safe.get('rest_connected') else '연결 대기'} "
        f"| {'정상' if safe.get('websocket_connected') else '연결 대기'} "
        f"| {'ON' if safe.get('kill_switch') else 'OFF'} |",
        "",
        "### 데이터 신선도",
        "",
        "| 마지막 시세 | 마지막 확정 캔들 | 마지막 잔고 대조 | 마지막 정상 루프 | 실행 커밋 |",
        "|---|---|---|---|---|",
        f"| {_value(safe.get('last_quote_at'))} | {_value(safe.get('last_candle_at'))} "
        f"| {_value(safe.get('last_account_sync'))} | {_value(safe.get('last_loop_at'))} "
        f"| `{_value(safe.get('running_commit'))}` |",
        "",
        "### 전략 및 포지션",
        "",
        "| 마켓 | 현재가 | 24시간 | 일봉 추세 | 4시간 돌파 | 신호 | 차단 사유 | 보유 | 투자 비중 | 수익률 | 손절 거리 |",
        "|---|---:|---:|---|---|---|---|---|---:|---:|---:|",
    ]
    markets = safe.get("markets", [])
    if markets:
        for market in markets:
            lines.append(
                f"| {_value(market.get('market'))} | {_value(market.get('price'))} "
                f"| {_value(market.get('change_24h_pct'))} "
                f"| {_value(market.get('daily_trend'))} "
                f"| {_value(market.get('four_hour_breakout'))} "
                f"| {_value(market.get('signal'))} | {_value(market.get('blocker'))} "
                f"| {'예' if market.get('position_open') else '아니오'} "
                f"| {_value(market.get('position_exposure_pct'))} "
                f"| {_value(market.get('return_pct'))} "
                f"| {_value(market.get('stop_distance_pct'))} |"
            )
    else:
        lines.append("| - | - | - | - | - | - | 실거래 미연결 | 아니오 | - | - | - |")

    lines += [
        "",
        "### 계좌 위험 — 금액 비공개",
        "",
        "| 총 투자 비중 | 계좌 고점 대비 낙폭 |",
        "|---:|---:|",
        f"| {_value(safe.get('total_exposure_pct'))} | {_value(safe.get('drawdown_pct'))} |",
        "",
        "## 최근 3일 이벤트",
        "",
        "| 시각 | 유형 | 마켓 | 사유 |",
        "|---|---|---|---|",
    ]
    visible = list(events)[-100:]
    if visible:
        for event in reversed(visible):
            lines.append(
                f"| {_value(event.get('timestamp'))} | {_value(event.get('type'))} "
                f"| {_value(event.get('market'))} | {_value(event.get('reason'))} |"
            )
    else:
        lines.append("| - | - | - | 기록 없음 |")
    lines += [
        "",
        "> 정확한 총자산·원화 잔고·코인 수량·API 인증정보·허용 IP는 공개하지 않습니다.",
        "",
    ]
    return "\n".join(lines)
