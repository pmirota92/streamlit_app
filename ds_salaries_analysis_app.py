import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import pandas as pd  # pip install pandas openpyxl
import country_converter as coco
import numpy as np
import plotly.graph_objects as go

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Salaries in 2020-2022", page_icon=":bar_chart:", layout="wide")

# ---- MAINPAGE ----
st.title(":bar_chart: Salaries of jobs in the Data Science domain")
st.markdown("##")
st.markdown("""
This app performs simple salaries analysis in the Data Science domain!
* **Python libraries:** plotly, pandas, streamlit
* **Data source:** [Kaggle](https://www.kaggle.com/datasets/ruchi798/data-science-job-salaries/download?datasetVersionNumber=1).
""")

# ---- READ EXCEL ----
# @st.cache(allow_output_mutation=True)
def get_data_from_excel():
    df = pd.read_excel(
            io="ds_salaries.xlsx",
            engine="openpyxl",
            sheet_name="ds_salaries",
            usecols="A:K",
            nrows=1000,
    )
    df['experience_level'] = df['experience_level'].replace({'EN': 'Entry-level/Junior', 'MI': 'Mid-level/Intermediate', 'SE': 'Senior-level/Expert', 'EX': 'Executive-level/Director'})
    # Add 'hour' column to dataframe
    # df["work_year"] = pd.to_datetime(df["work_year"]).dt.year
    return df

df = get_data_from_excel()

year_list = list(df['work_year'].unique())

# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")

selected_year = st.sidebar.multiselect(
     "Select Year:",
    options=df["work_year"].unique(),
    default=df["work_year"].unique())

job = st.sidebar.multiselect(
    "Select Job:",
    options=df["job_title"].unique(),
    default=df["job_title"].unique()
)

location= st.sidebar.multiselect(
    "Select Company Location:",
    options=df["company_location"].unique(),
    default=df["company_location"].unique()
)

df_selection = df.query("work_year == @selected_year  & company_location == @location & job_title == @job")

# ---- MAINPAGE ----

# TOP KPI's
Average_Salaries = round(df["salary_in_usd"].mean(),2)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Average:")
    st.subheader(f"$ {Average_Salaries:,}")

st.write('Data Dimension: ' + str(df.shape[0]) + ' rows and ' + str(df.shape[1]) + ' columns.')
job_counts= df['job_title'].value_counts().size
st.write('There is ' + str(job_counts)+ ' job titles in the dataset.')
st.markdown("""
There are **3 sizes of the company** under variable (company_size):
* **S:** less than 50 employees (small),
* **M:** 50 to 250 employees (medium),
* **L:** more than 250 employees (large).
""")

st.markdown("""
There are **4 type of employment** for the role:
* **PT:** Part-time,
* **FT:** Full-time,
* **CT:** Contract,
* **FL:** Freelance.
""")

st.dataframe(df_selection)

left_column, middle_column, right_column = st.columns(3)
left_column.subheader("Details for 2020")
left_column.dataframe(df[(df['work_year']==2020)]['salary_in_usd'].describe())
middle_column.subheader("Details for 2021")
middle_column.dataframe(df[(df['work_year']==2021)]['salary_in_usd'].describe())
right_column.subheader("Details for 2022")
right_column.dataframe(df[(df['work_year']==2022)]['salary_in_usd'].describe())

# Experience Level for total [PIE CHART]
ex_level = df['experience_level'].value_counts()
figExpSize = px.pie(df, values=ex_level, names=df['experience_level'].unique(), title="<b>Pie chart on Experience Level for total</b>")

st.plotly_chart(figExpSize)
st.markdown("""From pie chart, we can see that **Senior-level/Expert** (46%) 
is the most popular experience level in this dataset, and **Mid-level/Intermediate** ranked the next.
There's only 4.28% of **Executive-level/Director**.""")

# Experience Level for years [BAR CHART]
ex_level_by_years= df.groupby(by=["work_year", 'experience_level']).size().reset_index()
ex_level_by_years.rename(columns={0: 'Values'}, inplace=True)
ex_level_by_years = ex_level_by_years.pivot_table(index="work_year", values='Values', columns='experience_level')

st.dataframe(ex_level_by_years)
figExpSizeYear = px.bar(ex_level_by_years, x=["2020","2021", "2022"], 
                        y=['Entry-level/Junior', 'Mid-level/Intermediate', 'Senior-level/Expert','Executive-level/Director'], 
                        color_discrete_sequence=px.colors.sequential.OrRd, title='Pie chart on Experience Level for years')
figExpSizeYear.update_layout(
    xaxis_title="Year",
    yaxis_title="Count",
    font = dict(size=14,family="Franklin Gothic"))
st.plotly_chart(figExpSizeYear)
st.markdown("""We can notice that **Senior-level/Expert** is the most popular experience level in 2022, 
and **Mid-level/Intermediate** was the most popular in 2021.
The least popular type is the **Executive-level/Directior**.""")
# Top job title
job_title_top = df_selection['job_title'].value_counts()[:10]

fig_top_job = px.bar(y=job_title_top.values,
             x=job_title_top.index,
             color = job_title_top.index,
             color_discrete_sequence=px.colors.sequential.OrRd,
             text=job_title_top.values,
             title="<b>Top 10 Job Titles</b>")
fig_top_job.update_layout(
    xaxis_title="Job Titles",
    yaxis_title="Count",
    font = dict(size=14,family="Franklin Gothic"))
fig_top_job.update_layout(legend=dict(
    title="Job Titles"
))
st.plotly_chart(fig_top_job)

st.markdown("""We can notice that **Data Scientist**, 
**Data Engineer** and **Data Analyst** are top 3 frequent job titles almost in each year.""")

# Top employee residence
residence = df_selection['employee_residence'].value_counts()
top10_employee_location = residence[:10]
fig_top_residence = px.bar(y=top10_employee_location.values,
             x=top10_employee_location.index,
             color = top10_employee_location.index,
             color_discrete_sequence=px.colors.sequential.OrRd,
             text=top10_employee_location.values,
             title= "<b>Top 10 Location of Employee</b>"
            )
fig_top_residence.update_layout(
    xaxis_title="Location of Employee",
    yaxis_title="Count",
    legend={"title": "Locations"},
    font = dict(size=14,family="Franklin Gothic")
)

st.plotly_chart(fig_top_residence)

converted_country = coco.convert(names=df['employee_residence'], to="ISO3")
df['employee_residence'] = converted_country
residence2 = df['employee_residence'].value_counts()
fig_map = px.choropleth(locations=residence2.index,
                    color=residence2.values,
                    color_continuous_scale=px.colors.sequential.OrRd,
                    title = "<b>Employee Loaction Distribution Map</b>")

st.plotly_chart(fig_map)

st.subheader("**Salary in USD**")
#Salary in USD by company locations
st.markdown("""For Total we can see that the highest average salary is in Russia and USA. Moreover, the increase in average wages 
is directly proportional to the level of experience. """)
Salaries = (
    df_selection.groupby(by=["company_location"]).mean([["salary_in_usd"]]).sort_values(by="salary_in_usd", ascending =True).tail(10)
)
fig_salaries = px.bar(
    Salaries,
    x="salary_in_usd",
    y=Salaries.index,
    text=np.round([num / 1000 for num in Salaries["salary_in_usd"]], 2),
    orientation="h",
    title="<b>Salaries by Locations</b>",
    color_discrete_sequence=['#98140B'],
    template="plotly_white",

)
fig_salaries.update_layout(
    xaxis_title="Average Salary in USD (k)",
    yaxis_title="Company Location",
    font = dict(size=14,family="Franklin Gothic"))

#Salary in USD by experience level
EX = df_selection.loc[(df_selection['experience_level'] == 'Executive-level/Director')]
SE = df_selection.loc[(df_selection['experience_level'] == 'Senior-level/Expert')]
MI = df_selection.loc[(df_selection['experience_level'] == 'Mid-level/Intermediate')]
EN = df_selection.loc[(df_selection['experience_level'] == 'Entry-level/Junior')]

experience_salary = pd.DataFrame(columns=['Executive-level/Director','Senior-level/Expert','Mid-level/Intermediate', 'Entry-level/Junior'])
experience_salary['Executive-level/Director'] = EX.groupby('experience_level').mean('salary_in_usd')['salary_in_usd'].values
experience_salary['Senior-level/Expert'] = SE.groupby('experience_level').mean('salary_in_usd')['salary_in_usd'].values
experience_salary['Mid-level/Intermediate'] = MI.groupby('experience_level').mean('salary_in_usd')['salary_in_usd'].values
experience_salary['Entry-level/Junior'] = EN.groupby('experience_level').mean('salary_in_usd')['salary_in_usd'].values


fig_salaries_perExp = px.bar(
    x=experience_salary.values.tolist()[0],
    y= experience_salary.columns,
    text= np.round([num/1000 for num in experience_salary.values.tolist()[0]],2),
    orientation="h",
    title="<b>Salaries by Experience Level</b>",
    color_discrete_sequence=['#98140B'],
)

fig_salaries_perExp.update_layout(
    xaxis_title="Average Salary in USD (k)",
    yaxis_title="Experience Level",
    font = dict(size=14,family="Franklin Gothic"))

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_salaries, use_container_width=True)
right_column.plotly_chart(fig_salaries_perExp, use_container_width=True)


##############################
Job_line = (
    df_selection.groupby(by=["job_title"]).mean([["salary_in_usd"]]).sort_values(by="salary_in_usd", ascending =True).tail(16)
)
fig_line = px.bar(
        Job_line, #Data Frame
        x = "salary_in_usd", #Columns from the data frame
        y = Job_line.index,
        color_discrete_sequence=['#98140B'],
        title = "<b>Average salary for the most popular job positions</b>"
    )
fig_line.update_layout(
    xaxis_title="Average Salary in USD (k)",
    yaxis_title="Job Position",
    font = dict(size=14,family="Franklin Gothic"))
st.plotly_chart(fig_line)
##############################

fig_categ = px.scatter(
    df_selection,
    x="salary_in_usd",
    y="job_title",
    color="experience_level",
    title="<b>Salaries by Job Title and Experience Level</b>",
    color_discrete_sequence= px.colors.sequential.Plasma_r)

fig_categ.update_traces(marker_size=10)

fig_categ.update_layout(
    xaxis_title="Salary in USD (k)",
    yaxis_title="Job Title",
    legend={"title":"Experience Level"},
    font = dict(size=14,family="Franklin Gothic"))
st.plotly_chart(fig_categ)

st.subheader("**Salary distribution**")

salaries_perCompany = (df_selection.groupby(by=["company_size"]).sum()[["salary_in_usd"]])
fig_size = px.histogram(df_selection, x="salary_in_usd", color="company_size",
                   marginal="box", # or violin, rug
                   hover_data=df_selection.columns,
                   title= "<b>Salary distribution by Company Size</b>",
                   color_discrete_sequence = px.colors.sequential.Plasma_r)

fig_size.update_layout(
    xaxis_title="Salary in USD (k)",
    yaxis_title="Count",
    legend={"title":"Company Size"} ,
    font = dict(size=14,family="Franklin Gothic"))
st.plotly_chart(fig_size)
st.markdown("""The distribution is right-skewed. It is the distribution with the longer 
right tail of the distribution, which means that we have a lot of observations that take values less than the mean.""")

