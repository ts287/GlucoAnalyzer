import streamlit as st
import pandas as pd
import plotly.express as px
from databricks.sdk import WorkspaceClient
from io import BytesIO
import streamlit.components.v1 as components

# PAGE SETUP
st.set_page_config(
    page_title="GlucoAnalyzer",
    page_icon="🩸",
    layout="wide"
)

#st.title("🩸 GlucoAnalyzer")
st.markdown("<h1 style='text-align: center'>🩸 GlucoAnalyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center'>Explore glucose, heart rate, temperature, and food data.</p>", unsafe_allow_html=True)

#st.write(
    #"Explore glucose, heart rate, temperature, and food data."
#)

# DATABRICKS CLIENT
w = WorkspaceClient()


# DATABRICKS FILE LOADER
def load_csv(file_path, header=0):
    response = w.files.download(file_path)

    return pd.read_csv(
        BytesIO(response.contents.read()),
        header=header
    )


# SIDEBAR / PARTICIPANT SELECTION
st.sidebar.header("Data Selection")

participant = st.sidebar.selectbox(
    "Participant",
    ["001", "002", "003", "004", "005"]
)


# FILE PATHS
base_path = "/Volumes/workspace/default/physionet_1/"

dexcom_path = f"{base_path}Dexcom_{participant}.csv"
hr_path = f"{base_path}HR_{participant}.csv"
temp_path = f"{base_path}TEMP_{participant}.csv"
food_path = f"{base_path}Food_Log_{participant}.csv"


# LOAD GLUCOSE DATA
raw_glucose = load_csv(
    dexcom_path,
    header=None
)

glucose_data = raw_glucose[
    raw_glucose[2] == "EGV" #Estimated Glucose Value
].copy()

glucose_data["timestamp"] = pd.to_datetime(
    glucose_data[1],
    errors="coerce"
)

glucose_data["glucose"] = pd.to_numeric(
    glucose_data[7],
    errors="coerce"
)

glucose_df = glucose_data[
    ["timestamp", "glucose"]
].dropna()

glucose_df = glucose_df.sort_values(
    "timestamp"
)


# LOAD HEART RATE DATA
hr_df = load_csv(
    hr_path,
    header=None
)

hr_df = hr_df.dropna(
    axis=1,
    how="all"
)

hr_df = hr_df.iloc[:, :2]

hr_df.columns = [
    "datetime",
    "hr"
]

hr_df = hr_df[
    hr_df["datetime"] != "datetime"
]

hr_df["datetime"] = pd.to_datetime(
    hr_df["datetime"],
    errors="coerce"
)

hr_df["hr"] = pd.to_numeric(
    hr_df["hr"],
    errors="coerce"
)

hr_df = hr_df[
    ["datetime", "hr"]
].dropna()

hr_df = hr_df.sort_values(
    "datetime"
)


# LOAD TEMPERATURE DATA
temp_df = load_csv(
    temp_path,
    header=None
)

temp_df = temp_df.dropna(
    axis=1,
    how="all"
)

temp_df = temp_df.iloc[:, :2]

temp_df.columns = [
    "datetime",
    "temp"
]

temp_df = temp_df[
    temp_df["datetime"] != "datetime"
]

temp_df["datetime"] = pd.to_datetime(
    temp_df["datetime"],
    errors="coerce"
)

temp_df["temp"] = pd.to_numeric(
    temp_df["temp"],
    errors="coerce"
)

temp_df = temp_df[
    ["datetime", "temp"]
].dropna()

temp_df = temp_df.sort_values(
    "datetime"
)


# LOAD FOOD DATA
food_df = load_csv(
    food_path,
    header=None
)

food_df = food_df.dropna(
    axis=1,
    how="all"
)


# PARTICIPANT 003 HAS A DIFFERENT FOOD FILE FORMAT
if participant == "003":

    food_columns = [
        "date",
        "time",
        "time_begin",
        "logged_food",
        "amount",
        "unit",
        "searched_food",
        "calorie",
        "total_carb",
        "dietary_fiber",
        "sugar",
        "protein",
        "total_fat"
    ]

else:

    food_columns = [
        "date",
        "time",
        "time_begin",
        "time_end",
        "logged_food",
        "amount",
        "unit",
        "searched_food",
        "calorie",
        "total_carb",
        "dietary_fiber",
        "sugar",
        "protein",
        "total_fat"
    ]


# MAKE COLUMN COUNT MATCH
if len(food_df.columns) < len(food_columns):

    for i in range(
        len(food_df.columns),
        len(food_columns)
    ):
        food_df[i] = None

elif len(food_df.columns) > len(food_columns):

    food_df = food_df.iloc[
        :, :len(food_columns)
    ]

food_df.columns = food_columns


# REMOVE HEADER ROW IF PRESENT
food_df = food_df[
    food_df["date"] != "date"
]


# CONVERT FOOD DATA TYPES
food_df["time_begin"] = pd.to_datetime(
    food_df["time_begin"],
    errors="coerce"
)

food_df["amount"] = pd.to_numeric(
    food_df["amount"],
    errors="coerce"
)

food_df["calorie"] = pd.to_numeric(
    food_df["calorie"],
    errors="coerce"
)

food_df["total_carb"] = pd.to_numeric(
    food_df["total_carb"],
    errors="coerce"
)

food_df["sugar"] = pd.to_numeric(
    food_df["sugar"],
    errors="coerce"
)

food_df = food_df.dropna(
    subset=["time_begin"]
)

food_df = food_df.sort_values(
    "time_begin"
)


# DATE SELECTION
available_dates = sorted(
    glucose_df["timestamp"].dt.date.unique()
)

selected_date = st.sidebar.date_input(
    "Date",
    value=available_dates[0],
    min_value=available_dates[0],
    max_value=available_dates[-1]
)


# TIME SELECTION
selected_time = st.sidebar.time_input(
    "Time",
    value=pd.Timestamp(
        "12:00:00"
    ).time()
)

selected_datetime = pd.Timestamp(
    f"{selected_date} {selected_time}"
)


# FIND CLOSEST GLUCOSE
glucose_differences = (
    glucose_df["timestamp"]
    - selected_datetime
).abs()

closest_glucose_index = (
    glucose_differences.idxmin()
)

closest_glucose = glucose_df.loc[
    closest_glucose_index
]

glucose_value = closest_glucose["glucose"]


# FIND CLOSEST HEART RATE
hr_differences = (
    hr_df["datetime"]
    - selected_datetime
).abs()

closest_hr_index = (
    hr_differences.idxmin()
)

closest_hr = hr_df.loc[
    closest_hr_index
]

heart_rate = closest_hr["hr"]


# FIND CLOSEST TEMPERATURE
temp_differences = (
    temp_df["datetime"]
    - selected_datetime
).abs()

closest_temp_index = (
    temp_differences.idxmin()
)

closest_temp = temp_df.loc[
    closest_temp_index
]

temperature = closest_temp["temp"]


# FIND FOOD AROUND SELECTED TIME
food_start = (
    selected_datetime
    - pd.Timedelta(hours=2)
)

food_end = (
    selected_datetime
    + pd.Timedelta(minutes=30)
)

nearby_food = food_df[
    (food_df["time_begin"] >= food_start)
    &
    (food_df["time_begin"] <= food_end)
].copy()

nearby_food = nearby_food.sort_values(
    "time_begin"
)


# HEADER
st.subheader(
    f"Participant {participant} • "
    f"{selected_datetime.strftime('%B %d, %Y at %I:%M %p')}"
)


# METRICS
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        height: 150px;
        border: 1px solid #e5e7eb;
    }

    .metric-icon {
        font-size: 42px;
        line-height: 1;
        margin-bottom: 10px;
    }

    .metric-label {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .metric-value {
        font-size: 24px;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">🩸</div>
            <div class="metric-label">Glucose</div>
            <div class="metric-value">
                {glucose_value:.0f} mg/dL
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">❤️</div>
            <div class="metric-label">Heart Rate</div>
            <div class="metric-value">
                {heart_rate:.1f} BPM
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">🌡️</div>
            <div class="metric-label">Skin Temperature</div>
            <div class="metric-value">
                {temperature:.2f} °C
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# FOOD SECTION
st.subheader("🍽️ Food Around This Time")

if nearby_food.empty:

    st.info(
        "No food was logged around this time."
    )

else:

    for _, food in nearby_food.iterrows():

        food_name = food["logged_food"]
        amount = food["amount"]
        unit = food["unit"]

        food_time = food[
            "time_begin"
        ].strftime("%I:%M %p")

        if pd.isna(amount):

            amount_text = ""

        elif pd.isna(unit):

            amount_text = f"{amount:g}"

        else:

            amount_text = f"{amount:g} {unit}"

        st.write(
            f"**{food_time} — {food_name}** "
            f"{amount_text}"
        )

        nutrition = []

        if pd.notna(food["calorie"]):

            nutrition.append(
                f"{food['calorie']:.0f} cal"
            )

        if pd.notna(food["total_carb"]):

            nutrition.append(
                f"{food['total_carb']:.1f}g carbs"
            )

        if pd.notna(food["sugar"]):

            nutrition.append(
                f"{food['sugar']:.1f}g sugar"
            )

        if nutrition:

            st.caption(
                " • ".join(nutrition)
            )


# ADD FOOD
st.subheader("➕ Add Food")

if "added_food" not in st.session_state:

    st.session_state.added_food = []

food_name = st.text_input(
    "Food",
    placeholder="e.g. Apple"
)

food_amount = st.text_input(
    "Amount",
    placeholder="e.g. 1 medium"
)

if st.button("Add Food"):

    if food_name.strip():

        st.session_state.added_food.append(
            {
                "time": selected_datetime,
                "food": food_name,
                "amount": food_amount
            }
        )

        st.success(
            f"Added {food_name}!"
        )

    else:

        st.warning(
            "Enter a food first."
        )


# USER-ADDED FOODS
if st.session_state.added_food:

    st.write(
        "**Foods you added:**"
    )

    for item in st.session_state.added_food:

        st.write(
            f"• {item['food']} "
            f"{item['amount']} "
            f"at "
            f"{item['time'].strftime('%I:%M %p')}"
        )


# BLOOD GLUCOSE GRAPH
st.subheader(
    "🩸 Blood Glucose Throughout the Day"
)

selected_glucose = glucose_df[
    glucose_df["timestamp"].dt.date
    == selected_date
]

if selected_glucose.empty:

    st.warning(
        "No glucose data is available "
        "for this date."
    )

else:

    fig = px.line(
        selected_glucose,
        x="timestamp",
        y="glucose",
        labels={
            "timestamp": "Time",
            "glucose": "Glucose (mg/dL)"
        }
    )

    fig.update_layout(
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# AI AGENT / GENIE
st.subheader("🤖 Ask any questions you have to the blood sugar analyzer agent")

st.write(
    "Ask questions about your glucose, food, "
    "and wearable data."
)

components.html(
    """
    <iframe
        src="https://dbc-e2090bdf-21c2.cloud.databricks.com/embed/genie/rooms/01f1bf5c969c11a0a96b7dd99a3a3f5f?o=7474652017890318"
        width="100%"
        height="600"
        frameborder="0"
        allow="clipboard-write">
    </iframe>
    """,
    height=620,
    scrolling=True


)


# ABOUT
with st.expander("About GlucoAnalyzer"):

    st.write(
        "GlucoAnalyzer is a prototype for exploring "
        "wearable glucose, heart rate, temperature, "
        "and food data from the PhysioNet Big Ideas "
        "Glycemic-Wearable dataset."
    )