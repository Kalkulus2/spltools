import spltools
import streamlit as st
st.set_page_config(layout="wide")

st.title("spltools")
st.header("Battle configuration summarizer")
st.text("")


@st.cache_resource
def get_card_data():
    return spltools.get_card_data()


def generate_summary():
    bqid = str(st.session_state.bqid_key).strip()
    if "/" in bqid:
        bqid = bqid.split("/")[-1]
    if "?" in bqid:
        bqid = bqid.split("?")[0]
    try:
        b = spltools.Battle(bqid, card_data=st.session_state.card_data)
        st.session_state['battle_summary'] = b.markdown_summary()
        st.session_state['battle_log'] = b.get_log(markdown=True)
    except Exception as E:
        print(E)
        st.session_state['battle_summary'] = None

st.session_state['card_data'] = get_card_data()

col1, col2 = st.columns([2, 1])
with col1:
    instr = "Enter battle queue id here"
    bqid_entry = st.text_input(instr,
                               placeholder=instr,
                               label_visibility='collapsed',
                               key='bqid_key',
                               on_change=generate_summary)
with col2:
    bqid_button = st.button("Run", on_click=generate_summary)
bsum_tab, log_tab, log_md_tab = st.tabs(["Battle Summary", "Battle Log",
                                         "Battle Log (Markdown)"])

if 'battle_summary' not in st.session_state:
    st.session_state['battle_summary'] = None


if st.session_state.battle_summary is not None:
    with bsum_tab:
        table = st.session_state.battle_summary.split("#")[0]
        teams = st.session_state.battle_summary.split("#")[1:]
        team1, team2 = [x for x in teams if x != '']
        team1 = team1.replace("\n", "").split()
        team2 = team2.replace("\n", "").split()
        st.markdown(table)
        st.subheader(" ".join([team1[0], team1[1]]))
        st.image(team1[2:])
        st.subheader(" ".join([team2[0], team2[1]]))
        st.image(team2[2:])
        st.header("Battle summary (Markdown)")
        st.code(st.session_state.battle_summary, language='python')
    with log_tab:
        st.header("Battle log")
        st.markdown(st.session_state.battle_log)
    with log_md_tab:
        st.code(st.session_state.battle_log, language='python')
