import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from io import StringIO
import boto3

from s3LoginDetails import s3_credentials

app = dash.Dash()

def createDfFromS3Csv(object_key):
	aws_id = s3_credentials['id']
	aws_secret = s3_credentials['secret']
	client = boto3.client('s3', aws_access_key_id=aws_id, aws_secret_access_key=aws_secret)
	csv_obj = client.get_object(Bucket='kaitusagedashboard', Key=object_key)
	body = csv_obj['Body']
	csv_string = body.read().decode('utf-8')
	df = pd.read_csv(StringIO(csv_string))
	return df

school_students_agg_df = createDfFromS3Csv('dashboard_backend/school_students_agg.csv')
school_names_df = createDfFromS3Csv('dashboard_backend/school_names.csv')
school_students_agg_df = school_students_agg_df.merge(school_names_df, on='SCHL_NO', how='left')
school_students_agg_df = school_students_agg_df[school_students_agg_df['SCHL_NM']!='KAIT School']

school_assessments_agg_df = createDfFromS3Csv('dashboard_backend/school_assessments_agg.csv')
school_assessments_agg_df = school_assessments_agg_df.merge(school_names_df, on='SCHL_NO', how='left')
school_assessments_agg_df = school_assessments_agg_df[school_assessments_agg_df['SCHL_NM']!='KAIT School']

colors = {
    'background': 'FFFFFF',
    'text': '#A9A9A9'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='KAIT Usage Dashboard',
        style={
            'textAlign': 'center',
            'font-family': 'Calibri',
            'color': colors['text']
        }
    ),
    html.Div(children='Monitoring KAIT usage across deployments', style={
        'textAlign': 'center',
        'font-family': 'Calibri',
        'color': colors['text']
    }),
	dcc.Graph(
	    figure=go.Figure(
	        data=[
	            go.Bar(
	                x=school_students_agg_df['SCHL_NM'].tolist(),
	                y=school_students_agg_df['COUNT_STUDENTS'].tolist(),
	                text=school_students_agg_df['COUNT_STUDENTS'].tolist(),
	                textposition='auto',
	                name='Number of students',
	                marker=go.bar.Marker(
	                    color='rgb(53, 196, 72)'
	                )
	            )
	        ],
	        layout=go.Layout(
	            title='Number of students across schools',
	            showlegend=True,
	            legend=go.layout.Legend(
	                x=0,
	                y=1.0
	            ),
	            margin=go.layout.Margin(l=40, r=0, t=40, b=30)
	        )
	    ),
	    style={'height': '300px', 'width':'800px', 'font-family': 'Calibri'},
	    id='schoolsvsstudentsgraph'
	),
		dcc.Graph(
	    figure=go.Figure(
	        data=[
	            go.Bar(
	                x=school_assessments_agg_df['SCHL_NM'].tolist(),
	                y=school_assessments_agg_df['COUNT_ASSESSMENTS'].tolist(),
	                text=school_assessments_agg_df['COUNT_ASSESSMENTS'].tolist(),
	                textposition='auto',
	                name='Number of assessments',
	                marker=go.bar.Marker(
	                    color='rgb(55, 187, 204)'
	                )
	            )
	        ],
	        layout=go.Layout(
	            title='Number of assessments across schools',
	            showlegend=True,
	            legend=go.layout.Legend(
	                x=0,
	                y=1.0
	            ),
	            margin=go.layout.Margin(l=40, r=0, t=40, b=30)
	        )
	    ),
	    style={'height': '80vh', 'width':'800px', 'font-family': 'Calibri'},
	    id='schoolsvsassessments'
	) 
])

if __name__ == '__main__':
    app.run_server()