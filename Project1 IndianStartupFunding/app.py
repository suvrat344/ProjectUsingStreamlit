# Import necessary library
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set website title
st.set_page_config(layout="wide",page_title="Startup Analysis")

# Import dataset
df = pd.read_csv("startup_funding.csv")

df["Investors Name"] = df["Investors Name"].fillna("Undisclosed")

# Drop remark column
df.drop(columns=["Remarks"],inplace=True)

# Make sr no as index
df.set_index("Sr No",inplace=True)

# Rename column name
df.rename(columns={
    "Date dd/mm/yyyy":"date",
    "Startup Name":"startup",
    "Industry Vertical":"vertical",
    "SubVertical":"subvertical",
    "City  Location":"city",
    "Investors Name":"investors",
    "InvestmentnType":"round",
    "Amount in USD":"amount"
},inplace=True)

# Fill 0 in amount column in place of na
df["amount"] = df["amount"].fillna("0")

# Cleaning amount column
df["amount"] = df["amount"].str.replace(",","")
df["amount"] = df["amount"].str.replace("undisclosed","0")
df["amount"] = df["amount"].str.replace("unknown","0")
df["amount"] = df["amount"].str.replace("Undisclosed","0")
df = df[df["amount"].str.isdigit()]

# Change data type of amount column
df["amount"] = df["amount"].astype("float")

# convert dollar to inr
def to_inr(dollar):
    inr = dollar * 82.5
    return round(inr/10000000,2)
df["amount"] = df["amount"].apply(to_inr)

# Change data type of date column 
df["date"] = pd.to_datetime(df['date'], format='%d/%m/%Y',errors="coerce")
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month

# Drop all rows where na values present
df.dropna(subset=["date","startup","city","investors","round","amount"],inplace=True)

# Give title to the page
st.sidebar.title("Startup Funding Analysis")

# Make sidebar in the page
option = st.sidebar.selectbox("Select one",["Overall Analysis","StartUp","Investor"])

# Investor Details
def load_investor_detail(investor):
  st.title(investor)
  # load recent 5 investments of the investor
  last5_df = df[df["investors"].str.contains("investor")].head()[["date","startup","vertical","city","round","amount"]]
  st.subheader("Most Recent Investment")
  st.dataframe(last5_df)
  
  col1,col2 = st.columns(2)
  with col1:
    # Biggest Investment
    big_series = df[df["investors"].str.contains(investor)].groupby("startup")["amount"].sum().head().sort_values(ascending=False)
    st.subheader("Biggest Investment")
    fig,ax = plt.subplots()
    ax.bar(big_series.index,big_series.values)
    st.pyplot(fig)
  
  with col2:
    vertical_series = df[df["investors"].str.contains(investor)].groupby("vertical")["amount"].sum().head()
    st.subheader("Sector invested in")
    fig1,ax1 = plt.subplots()
    ax1.pie(vertical_series,labels=vertical_series.index,autopct="%0.01f")
    st.pyplot(fig1)
    
  year_series = df[df["investors"].str.contains(investor)].groupby("year")["amount"].sum()
  st.subheader("YoY Investment")
  fig2,ax2 = plt.subplots()
  ax2.plot(year_series.index,year_series.values)
  st.pyplot(fig2)


# Overall Analysis
def load_overall_analysis():
  st.title("Overall Analysis")
  
  col1,col2,col3,col4 = st.columns(4)
  
  with col1:
    # total inveted amount
    total = round(df["amount"].sum())
    st.metric("Total",str(total) + " CR")
  with col2:
    # maximum amount infused in startup
    max_funding = df.groupby("startup")["amount"].max().sort_values(ascending=False).head(n=1).values[0]
    st.metric("max",str(max_funding) + " CR")
  with col3:
    # average ticket size
    average_funding = round(df.groupby("startup")["amount"].sum().mean())
    st.metric("Average",str(average_funding) + " CR")
  with col4:
    # total funded startup
    num = df["startup"].nunique()
    st.metric("Funded Startup",str(num))
    
  st.header("MOM Graph")
  selected_option = st.selectbox("Select Type",["Total","Count"])
  if(selected_option == "Total"):
    temp_df = df.groupby(["year","month"])["amount"].sum().reset_index()
  else:
    temp_df = df.groupby(["year","month"])["amount"].count().reset_index()
  temp_df["x_axis"] = temp_df["month"].astype("str") + "-" + temp_df["year"].astype("str")
  fig3,ax3 = plt.subplots()
  ax3.plot(temp_df["x_axis"],temp_df["amount"])
  st.pyplot(fig3)
    
    
# Different option present in sidebar
if(option == "Overall Analysis"):
  load_overall_analysis()
elif(option == "StartUp"):
  st.sidebar.selectbox("Select StartUp",sorted(df["startup"].unique().tolist()))
  btn1 = st.sidebar.button("Find Startup Details")
  st.title("StartUp Analysis")
else:
  selected_investor = st.sidebar.selectbox("Select StartUp",sorted(set(df["investors"].str.split(",").sum())))
  btn2 = st.sidebar.button("Find Investors Details")
  if btn2:
    load_investor_detail(selected_investor)