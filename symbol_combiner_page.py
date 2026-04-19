import streamlit as st
import pandas as pd


def remove_suffix(ticker):
    return str(ticker).split('.')[0].strip()


def symbol_combiner_page():
    st.title("Symbol Combiner")
    st.caption("Upload two exchange CSV files, find symbols unique to each, combine and download.")

    # ── Upload ────────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        exchange_a_name = st.text_input("Exchange A name", value="Bybit")
        exchange_a_file = st.file_uploader(f"{exchange_a_name} CSV (needs 'Symbol' column)", type="csv", key="file_a")

    with col2:
        exchange_b_name = st.text_input("Exchange B name", value="Bitget")
        exchange_b_file = st.file_uploader(f"{exchange_b_name} CSV (needs 'Symbol' column)", type="csv", key="file_b")

    # ── Run ───────────────────────────────────────────────────────────────────
    ready = exchange_a_file and exchange_b_file
    if not ready:
        st.info("Upload both CSV files to enable the Compare button.")
        st.stop()

    if not st.button("Compare & Combine", type="primary"):
        st.stop()

    # ── Load ──────────────────────────────────────────────────────────────────
    try:
        df_a = pd.read_csv(exchange_a_file)
        df_b = pd.read_csv(exchange_b_file)
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        st.stop()

    for df, name in [(df_a, exchange_a_name), (df_b, exchange_b_name)]:
        if "Symbol" not in df.columns:
            st.error(f"'{name}' CSV is missing a 'Symbol' column. Found: {list(df.columns)}")
            st.stop()

    set_a = set(remove_suffix(t) for t in df_a["Symbol"].dropna())
    set_b = set(remove_suffix(t) for t in df_b["Symbol"].dropna())

    only_in_a = sorted(set_a - set_b)
    only_in_b = sorted(set_b - set_a)
    in_both   = sorted(set_a & set_b)

    # ── Stats ─────────────────────────────────────────────────────────────────
    st.divider()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(f"{exchange_a_name} total", len(set_a))
    c2.metric(f"{exchange_b_name} total", len(set_b))
    c3.metric(f"Only on {exchange_a_name}", len(only_in_a))
    c4.metric(f"Only on {exchange_b_name}", len(only_in_b))
    c5.metric("On both", len(in_both))

    # ── Combined DataFrame ────────────────────────────────────────────────────
    df_only_a   = pd.DataFrame({"Symbol": only_in_a, "Exchange": exchange_a_name})
    df_only_b   = pd.DataFrame({"Symbol": only_in_b, "Exchange": exchange_b_name})
    df_combined = (
        pd.concat([df_only_a, df_only_b], ignore_index=True)
        .sort_values("Symbol")
        .reset_index(drop=True)
    )

    st.subheader(f"Combined unique symbols — {len(df_combined)} rows")
    st.dataframe(df_combined, use_container_width=True, height=400)

    with st.expander(f"Only on {exchange_a_name} ({len(only_in_a)})"):
        st.dataframe(pd.DataFrame({"Symbol": only_in_a}), use_container_width=True)

    with st.expander(f"Only on {exchange_b_name} ({len(only_in_b)})"):
        st.dataframe(pd.DataFrame({"Symbol": only_in_b}), use_container_width=True)

    with st.expander(f"On both exchanges ({len(in_both)})"):
        st.dataframe(pd.DataFrame({"Symbol": in_both}), use_container_width=True)

    # ── Download ──────────────────────────────────────────────────────────────
    st.divider()
    csv_bytes = df_combined.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Download combined CSV",
        data=csv_bytes,
        file_name=f"{exchange_a_name}_{exchange_b_name}_Unique_Combined.csv",
        mime="text/csv",
    )
