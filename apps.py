import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

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
    st.write(pd.DataFrame(stats, index=[0]))

    st.subheader("🔮 Suggested Numbers Based on Frequency")
    top_main = pd.Series(all_nums).value_counts().head(10)
    top_powerball = numbers['Powerball'].value_counts().head(5)
    st.markdown("**Top 10 Frequent Main Numbers:**")
    st.write(list(top_main.index))
    st.markdown("**Top 5 Frequent Powerball Numbers:**")
    st.write(list(top_powerball.index))

    st.subheader("🎲 Smart Random Picks (Weighted by Frequency)")
    def weighted_random_choice(counter, size, max_num):
        items = list(counter.items())
        items = [item for item in items if item[0] <= max_num]
        nums, weights = zip(*items)
        return sorted(np.random.choice(nums, size=size, replace=False, p=np.array(weights)/sum(weights)))

    smart_main = weighted_random_choice(Counter(all_nums), 5, 69)
    smart_powerball = weighted_random_choice(Counter(numbers['Powerball']), 1, 26)[0]

    st.markdown(f"**AI-Weighted Pick:** {smart_main} + Powerball: {smart_powerball}")

else:
    st.info("⬆️ Please upload a Powerball CSV file to begin analysis.")
