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

mean = st.sidebar.number_input(u"Mean (\u03bc)", value=0.0, step=0.1, key="mean")

std = st.sidebar.number_input(u"Standard Deviation (\u03c3)", value=1.0, step=0.1, key="std")

dual_range = st.sidebar.checkbox("Dual range", value=False, key="dual_range")

col1, _, col2 = st.columns([5, 1, 5])

with col1:
    st.markdown("#### Region 1")

if dual_range:
    with col2:
        st.markdown("#### Region 2")

reg1_dir, reg1_lim, _, reg2_dir, reg2_lim = st.columns([2, 3, 1, 2, 3])

with reg1_dir:
    direction1 = st.selectbox("Direction", options=["<=", ">="], key="direction1", index=0)
with reg1_lim:
    limit1 = st.number_input("Limit", value=mean, step=0.1, key="limit1")

if dual_range:
    with reg2_dir:
        direction2 = st.selectbox("Direction", options=["<=", ">="], key="direction2", index=1)
    with reg2_lim:
        limit2 = st.number_input("Limit", value=mean, step=0.1, key="limit2")

range1 = Range(limit1, direction1)
if dual_range:
    range2 = Range(limit2, direction2)

custom_dist = stats.norm(loc=mean, scale=std)

x = custom_dist.rvs(size=10000)

st.divider()

result1, _, result2 = st.columns([5, 1, 5])

result1.markdown("##### Area of region 1:")
result1.markdown(f"##### :red[{area_under_curve(limit1, direction1): .4f}]")

if dual_range:
    result2.markdown("##### Area of region 2:")
    result2.markdown(f"##### :blue[{area_under_curve(limit2, direction2): .4f}]")

fig = ff.create_distplot([x], ['distplot'], curve_type='normal', show_hist=False, show_rug=False, colors=["black"])
x1, y1 = produce_values(fig, direction1, limit1)

if dual_range:
    x2, y2 = produce_values(fig, direction2, limit2)

# adds shaded area below the curve to the left of a limit
fig.add_scatter(x=x1, y=y1, fill="tozeroy", fillcolor="rgba(200,0,0,0.25)", line_color="rgba(0,0,0,0)")
if dual_range:
    fig.add_scatter(x=x2, y=y2, fill="tozeroy", fillcolor="rgba(0,0,200,0.25)", line_color="rgba(0,0,0,0)")


fig.update_layout(showlegend=False, title=dict(text=f"Normal Distribution (\u03bc={mean}, \u03c3={std})", font_size=18))
fig.update_yaxes(showticklabels=False)
fig.update_xaxes(range=[(mean - 3 * std) * 0.95, (mean + 3 * std) * 1.05], tickfont_size=18)

if dual_range:
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
