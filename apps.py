import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

st.set_page_config(layout="wide")
st.title("🎯 Powerball Winning Numbers Analysis & Prediction Tool")

# Upload CSV file
uploaded_file = st.file_uploader("Upload Powerball CSV Data", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = ['Draw Date', 'Winning Numbers', 'Multiplier']
    df['Draw Date'] = pd.to_datetime(df['Draw Date'])

    # Split the winning numbers
    numbers = df['Winning Numbers'].str.split(' ', expand=True).astype(int)
    numbers.columns = ['N1', 'N2', 'N3', 'N4', 'N5', 'Powerball']
    df = pd.concat([df, numbers], axis=1)

    # Filter by year or month
    st.sidebar.header("📆 Filter Draws")
    year_selected = st.sidebar.multiselect("Select Year(s)", options=sorted(df['Draw Date'].dt.year.unique()), default=sorted(df['Draw Date'].dt.year.unique()))
    month_selected = st.sidebar.multiselect("Select Month(s)", options=range(1, 13), default=list(range(1, 13)))
    df = df[df['Draw Date'].dt.year.isin(year_selected) & df['Draw Date'].dt.month.isin(month_selected)]
    numbers = df[['N1', 'N2', 'N3', 'N4', 'N5', 'Powerball']]

    st.subheader("📅 Draws Overview")
    st.write(df[['Draw Date', 'Winning Numbers', 'Multiplier']].tail(10))

    st.subheader("📊 Frequency of Main Numbers (1-69)")
    all_nums = numbers.drop(columns='Powerball').values.flatten()
    fig1, ax1 = plt.subplots()
    sns.histplot(all_nums, bins=69, kde=False, ax=ax1)
    ax1.set_title('Frequency of Main Numbers (1-69)')
    ax1.set_xlabel('Number')
    ax1.set_ylabel('Frequency')
    st.pyplot(fig1)

    st.subheader("🔴 Frequency of Powerball Numbers (1-26)")
    fig2, ax2 = plt.subplots()
    sns.histplot(numbers['Powerball'], bins=26, color='red', ax=ax2)
    ax2.set_title('Frequency of Powerball Numbers')
    ax2.set_xlabel('Powerball Number')
    ax2.set_ylabel('Frequency')
    st.pyplot(fig2)

    st.subheader("🌡️ Heatmap of Number Positions")
    heatmap_data = pd.DataFrame(0, index=range(1, 70), columns=['N1', 'N2', 'N3', 'N4', 'N5'])
    for i in range(1, 6):
        heatmap_data[f'N{i}'] = numbers[f'N{i}'].value_counts().reindex(range(1, 70), fill_value=0)

    fig3, ax3 = plt.subplots(figsize=(10, 8))
    sns.heatmap(heatmap_data, cmap='Blues', ax=ax3)
    ax3.set_title('Heatmap of Number Positions (1-69)')
    st.pyplot(fig3)

    st.subheader("📈 Statistical Summary")
    stats = {
        'Most Common Main Number': pd.Series(all_nums).mode().iloc[0],
        'Most Common Powerball': numbers['Powerball'].mode().iloc[0],
        'Average Main Number': np.mean(all_nums),
        'Average Powerball': np.mean(numbers['Powerball']),
        'Standard Deviation (Main)': np.std(all_nums),
        'Standard Deviation (Powerball)': np.std(numbers['Powerball'])
    }
    stats_df = pd.DataFrame(stats, index=[0])
    st.write(stats_df)

    st.subheader("🔮 Suggested Numbers Based on Frequency")
    top_main = pd.Series(all_nums).value_counts().head(5).sort_index()
    top_powerball = numbers['Powerball'].value_counts().head(1).sort_index()
    st.markdown("**Most Frequent Main Numbers:**")
    st.write(list(top_main.index))
    st.markdown("**Most Frequent Powerball:**")
    st.write(int(top_powerball.index[0]))

    st.subheader("🎲 Random Smart Pick Based on Top Frequencies")
    random_pick = np.random.choice(top_main.index, 5, replace=False)
    power_pick = int(top_powerball.index[0])
    st.markdown(f"**Your Suggested Pick:** {sorted(random_pick)} + Powerball: {power_pick}")

    # Downloadable report
    st.subheader("📥 Download Statistical Report")
    buffer = BytesIO()
    stats_df.to_csv(buffer, index=False)
    st.download_button(label="Download CSV Report", data=buffer.getvalue(), file_name="powerball_stats_report.csv", mime="text/csv")

else:
    st.info("⬆️ Please upload a Powerball CSV file to begin analysis.")
