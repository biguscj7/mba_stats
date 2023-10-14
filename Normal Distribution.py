import streamlit as st
from plotly import figure_factory as ff
from plotly import graph_objects as go
from scipy import stats
from collections import namedtuple

Range = namedtuple("Range", ["limit", "direction"])


def produce_values(fig: go.Figure, direction: str, limit: float) -> tuple:
    if direction == "<=":
        plot_x = [xc for xc in fig.data[0].x if xc < limit]
        plot_y = fig.data[0].y[:len(plot_x)]
    else:
        plot_x = [xc for xc in fig.data[0].x if xc > limit]
        plot_y = fig.data[0].y[-len(plot_x):]

    return plot_x, plot_y


def area_under_curve(limit: float, direction: str) -> float:
    if direction == "<=":
        return custom_dist.cdf(limit)
    else:
        return 1 - custom_dist.cdf(limit)


def separate_areas(limit1: float, limit2: float, direction1: str, direction2: str) -> str:
    area1 = area_under_curve(limit1, direction1)
    area2 = area_under_curve(limit2, direction2)
    return f"### Total area of both regions: {area1 + area2: .4f}"


def overlapping_areas_same_direction(limit1: float, limit2: float, direction1: str, direction2: str) -> str:
    area1 = area_under_curve(limit1, direction1)
    area2 = area_under_curve(limit2, direction2)
    if area1 > area2:
        return f"### Area 1 exclusive: {abs(area2 - area1): .4f}"
    else:
        return f"### Area 2 exclusive: {abs(area1 - area2): .4f}"


def overlapping_areas_opposite_direction(limit1: float, limit2: float) -> str:
    return f"### Area of overlap: {abs(area_under_curve(limit1, '<=') - area_under_curve(limit2, '<=')): .4f}"


st.title("Normal Distribution plotter")

mean_col, sd_col = st.columns(2)

with mean_col:
    mean = st.number_input("Mean", value=0.0, step=0.1, key="mean")
with sd_col:
    std = st.number_input("Standard Deviation", value=1.0, step=0.1, key="std")

st.divider()

reg1_col, _, reg2_col = st.columns([4, 2, 4])

with reg1_col:
    st.markdown("### :red[Region 1]")
    direction1 = st.selectbox("Direction 1", options=["<=", ">="], key="direction1", index=0)
    limit1 = st.number_input("Limit 1", value=mean, step=0.1, key="limit1")


with reg2_col:
    st.markdown("### :blue[Region 2]")
    direction2 = st.selectbox("Direction 2", options=["<=", ">="], key="direction2", index=1)
    limit2 = st.number_input("Limit 2", value=mean, step=0.1, key="limit2")


range1 = Range(limit1, direction1)
range2 = Range(limit2, direction2)

st.divider()

custom_dist = stats.norm(loc=mean, scale=std)

x = custom_dist.rvs(size=5000)

reg1_col.markdown(f"##### :red[Area of region 1: {area_under_curve(limit1, direction1): .4f}]")
reg2_col.markdown(f"##### :blue[Area of region 2: {area_under_curve(limit2, direction2): .4f}]")

fig = ff.create_distplot([x], ['distplot'], curve_type='normal', show_hist=False, show_rug=False, colors=["white"])
x1, y1 = produce_values(fig, direction1, limit1)
x2, y2 = produce_values(fig, direction2, limit2)

# adds shaded area below the curve to the left of a limit
fig.add_scatter(x=x2, y=y2, fill="tozeroy", fillcolor="rgba(0,0,200,0.25)", line_color="rgba(0,0,0,0)")
fig.add_scatter(x=x1, y=y1, fill="tozeroy", fillcolor="rgba(200,0,0,0.25)", line_color="rgba(0,0,0,0)")

fig.update_layout(showlegend=False)
fig.update_yaxes(showticklabels=False)
fig.update_xaxes(range=[mean - 3 * std, mean + 3 * std])

ranges = (range1, range2)

match ranges:
    case (x, y) if x.direction == y.direction:
        st.markdown(overlapping_areas_same_direction(limit1, limit2, direction1, direction2))
    case (x, y) if (x.limit >= y.limit) and (x.direction == "<="):  # overlap
        st.markdown(overlapping_areas_opposite_direction(x.limit, y.limit))
    case (x, y) if (y.limit >= x.limit) and (y.direction == "<="):  # overlap
        st.markdown(overlapping_areas_opposite_direction(x.limit, y.limit))
    case (x, y) if (x.limit <= y.limit) and (x.direction == "<="):  # no overlap
        st.markdown(separate_areas(x.limit, y.limit, x.direction, y.direction))
    case (x, y) if (y.limit <= x.limit) and (y.direction == "<="):  # no overlap
        st.markdown(separate_areas(y.limit, x.limit, y.direction, x.direction))
    case _:
        st.write("No match")

st.plotly_chart(fig, use_container_width=True)
