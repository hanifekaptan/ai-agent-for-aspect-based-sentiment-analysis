"""
Visualizations Module
Contains functions for displaying analysis results and charts.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io


def display_results(results, is_single=False):
    """
    Displays analysis results with visualizations.
    
    Args:
        results: API response containing analysis results.
        is_single (bool): Whether this is a single text analysis.
    """
    st.success("✅ Analysis completed!")
    
    items_submitted = results.get('items_submitted', 0)
    batches_sent = results.get('batches_sent', 0)
    duration = results.get('duration_seconds', 0)
    items = results.get('results', [])
    
    _display_summary_metrics(items_submitted, batches_sent, duration, items)
    
    st.divider()
    
    all_aspects = _aggregate_aspects(items)
    
    if not all_aspects:
        st.warning("⚠️ No aspects found!")
        return
    
    df_aspects = pd.DataFrame(all_aspects)
    
    _display_charts(df_aspects)
    
    st.divider()
    
    aspect_sentiment_matrix = _display_aspect_sentiment_matrix(df_aspects)
    
    st.divider()
    
    _display_detailed_results(items)
    
    _display_export_options(df_aspects, aspect_sentiment_matrix)


def _display_summary_metrics(items_submitted, batches_sent, duration, items):
    """Displays summary metrics at the top."""
    st.markdown("## 📊 Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📝 Items Processed", items_submitted)
    with col2:
        st.metric("📦 Batches", batches_sent)
    with col3:
        st.metric("⏱️ Duration (s)", f"{duration:.2f}")
    with col4:
        total_aspects = sum(len(item.get('aspects', [])) for item in items)
        st.metric("🎯 Total Aspects", total_aspects)


def _aggregate_aspects(items):
    """Aggregates all aspects from the items."""
    all_aspects = []
    for item in items:
        for aspect in item.get('aspects', []):
            all_aspects.append({
                'term': aspect.get('term', ''),
                'sentiment': aspect.get('sentiment', 'neutral')
            })
    return all_aspects


def _display_charts(df_aspects):
    """Displays sentiment and term frequency charts."""
    col_left, col_right = st.columns(2)
    
    with col_left:
        _display_sentiment_pie_chart(df_aspects)
    
    with col_right:
        _display_term_frequency_chart(df_aspects)


def _display_sentiment_pie_chart(df_aspects):
    """Displays the sentiment distribution pie chart."""
    st.markdown("### 😊 Sentiment Distribution")
    sentiment_counts = df_aspects['sentiment'].value_counts()
    
    fig_sentiment = go.Figure(data=[go.Pie(
        labels=sentiment_counts.index,
        values=sentiment_counts.values,
        hole=0.4,
        marker=dict(colors=['#2ecc71', '#e74c3c', '#95a5a6'])
    )])
    fig_sentiment.update_layout(height=350)
    st.plotly_chart(fig_sentiment, use_container_width=True)


def _display_term_frequency_chart(df_aspects):
    """Displays the most frequent aspects bar chart."""
    st.markdown("### 🏆 Most Frequent Aspects")
    term_counts = df_aspects['term'].value_counts().head(10)
    
    fig_terms = px.bar(
        x=term_counts.values,
        y=term_counts.index,
        orientation='h',
        labels={'x': 'Frequency', 'y': 'Aspect'},
        color=term_counts.values,
        color_continuous_scale='Blues'
    )
    fig_terms.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_terms, use_container_width=True)


def _display_aspect_sentiment_matrix(df_aspects):
    """Displays the aspect-sentiment matrix table."""
    st.markdown("### 📈 Aspect-Based Sentiment Analysis")
    
    aspect_sentiment_matrix = df_aspects.groupby(['term', 'sentiment']).size().unstack(fill_value=0)
    
    if 'positive' in aspect_sentiment_matrix.columns and 'negative' in aspect_sentiment_matrix.columns:
        aspect_sentiment_matrix['total'] = aspect_sentiment_matrix.sum(axis=1)
        aspect_sentiment_matrix['satisfaction_%'] = (
            aspect_sentiment_matrix['positive'] / aspect_sentiment_matrix['total'] * 100
        ).round(1)
        aspect_sentiment_matrix = aspect_sentiment_matrix.sort_values('satisfaction_%', ascending=False)
    
    st.dataframe(aspect_sentiment_matrix, use_container_width=True)
    
    return aspect_sentiment_matrix


def _display_detailed_results(items):
    """Displays detailed results in an expander."""
    with st.expander("🔍 Detailed Results", expanded=False):
        for idx, item in enumerate(items, 1):
            st.markdown(f"**#{item.get('id', idx)}**")
            aspects = item.get('aspects', [])
            
            if aspects:
                for aspect in aspects:
                    term = aspect.get('term', 'N/A')
                    sentiment = aspect.get('sentiment', 'neutral')
                    
                    sentiment_class = sentiment.lower()
                    st.markdown(
                        f"- **{term}**: <span class='{sentiment_class}'>{sentiment}</span>",
                        unsafe_allow_html=True
                    )
            else:
                st.markdown("_No aspects found_")
            
            st.divider()


def _display_export_options(df_aspects, aspect_sentiment_matrix):
    """Displays export buttons for CSV and Excel."""
    st.markdown("### 💾 Export")
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        csv_data = df_aspects.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="absa_results.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_exp2:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_aspects.to_excel(writer, sheet_name='Aspects', index=False)
            if isinstance(aspect_sentiment_matrix, pd.DataFrame):
                aspect_sentiment_matrix.to_excel(writer, sheet_name='Summary')
        
        st.download_button(
            label="📥 Download Excel",
            data=buffer.getvalue(),
            file_name="absa_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
