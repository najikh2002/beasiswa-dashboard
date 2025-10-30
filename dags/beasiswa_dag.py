from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'beasiswa_scraper',
    default_args=default_args,
    description='Scrape dan update data beasiswa Indonesia',
    schedule_interval='0 0 * * *',
    catchup=False,
)

# ✅ Import library berat di dalam fungsi agar tidak membuat DAG parse lambat
def scrape_beasiswa_data():
    import pandas as pd
    import os

    beasiswa_data = [
        {
            'nama': 'LPDP Beasiswa Pendidikan Indonesia',
            'jenjang': 'Master/PhD',
            'negara': 'Worldwide',
            'buka': '2024-03-01',
            'tutup': '2024-04-30',
            'url': 'https://lpdp.kemenkeu.go.id',
            'deskripsi': 'Beasiswa penuh untuk S2/S3 di universitas terbaik dunia'
        },
        {
            'nama': 'Chevening UK Scholarship',
            'jenjang': 'Master',
            'negara': 'UK',
            'buka': '2024-08-01',
            'tutup': '2024-11-07',
            'url': 'https://www.chevening.org',
            'deskripsi': 'Beasiswa pemerintah UK untuk S2 satu tahun'
        },
        {
            'nama': 'Australia Awards Scholarship',
            'jenjang': 'Master/PhD',
            'negara': 'Australia',
            'buka': '2024-02-01',
            'tutup': '2024-04-30',
            'url': 'https://www.australiaawardsindonesia.org',
            'deskripsi': 'Beasiswa pemerintah Australia untuk WNI'
        },
        {
            'nama': 'Fulbright PhD Scholarship',
            'jenjang': 'PhD',
            'negara': 'USA',
            'buka': '2024-02-01',
            'tutup': '2024-05-31',
            'url': 'https://www.aminef.or.id',
            'deskripsi': 'Beasiswa S3 di universitas Amerika Serikat'
        },
        {
            'nama': 'DAAD Scholarship',
            'jenjang': 'Master/PhD',
            'negara': 'Germany',
            'buka': '2024-08-01',
            'tutup': '2024-11-15',
            'url': 'https://www.daad.de',
            'deskripsi': 'Beasiswa dari pemerintah Jerman'
        },
        {
            'nama': 'Erasmus Mundus Joint Masters',
            'jenjang': 'Master',
            'negara': 'Europe',
            'buka': '2024-10-01',
            'tutup': '2025-01-15',
            'url': 'https://www.eacea.ec.europa.eu',
            'deskripsi': 'Beasiswa S2 di beberapa universitas Eropa'
        },
        {
            'nama': 'New Zealand ASEAN Scholars Awards',
            'jenjang': 'PhD',
            'negara': 'New Zealand',
            'buka': '2024-07-01',
            'tutup': '2024-10-01',
            'url': 'https://www.nzaseanscholars.org',
            'deskripsi': 'Beasiswa S3 di New Zealand untuk ASEAN'
        },
        {
            'nama': 'Monbukagakusho MEXT Scholarship',
            'jenjang': 'Master/PhD',
            'negara': 'Japan',
            'buka': '2024-04-01',
            'tutup': '2024-06-15',
            'url': 'https://www.id.emb-japan.go.jp',
            'deskripsi': 'Beasiswa pemerintah Jepang'
        },
        {
            'nama': 'Korean Government Scholarship (KGSP)',
            'jenjang': 'Master/PhD',
            'negara': 'South Korea',
            'buka': '2024-02-15',
            'tutup': '2024-03-31',
            'url': 'https://www.studyinkorea.go.kr',
            'deskripsi': 'Beasiswa pemerintah Korea Selatan'
        },
        {
            'nama': 'Chinese Government Scholarship',
            'jenjang': 'Master/PhD',
            'negara': 'China',
            'buka': '2024-01-01',
            'tutup': '2024-04-30',
            'url': 'https://www.campuschina.org',
            'deskripsi': 'Beasiswa dari pemerintah China'
        },
    ]
    
    df = pd.DataFrame(beasiswa_data)
    df['buka'] = pd.to_datetime(df['buka'])
    df['tutup'] = pd.to_datetime(df['tutup'])
    
    output_path = '/opt/airflow/data/beasiswa.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"Data berhasil disimpan: {len(df)} beasiswa")
    return output_path


def process_timeline():
    import pandas as pd
    import json
    from datetime import datetime

    df = pd.read_csv('/opt/airflow/data/beasiswa.csv')
    df['buka'] = pd.to_datetime(df['buka'])
    df['tutup'] = pd.to_datetime(df['tutup'])
    
    today = pd.Timestamp.now()
    
    def get_status(row):
        if today < row['buka']:
            days_until = (row['buka'] - today).days
            return f'Akan Buka ({days_until} hari lagi)'
        elif row['buka'] <= today <= row['tutup']:
            days_left = (row['tutup'] - today).days
            return f'Sedang Buka ({days_left} hari lagi)'
        else:
            return 'Sudah Tutup'
    
    df['status'] = df.apply(get_status, axis=1)
    df['hari_tersisa'] = df.apply(
        lambda row: (row['tutup'] - today).days if row['buka'] <= today <= row['tutup'] 
        else (row['buka'] - today).days if today < row['buka'] 
        else 0, 
        axis=1
    )
    
    output_path = '/opt/airflow/data/beasiswa_processed.csv'
    df.to_csv(output_path, index=False)
    
    stats = {
        'total_beasiswa': len(df),
        'sedang_buka': len(df[df['status'].str.contains('Sedang Buka')]),
        'akan_buka': len(df[df['status'].str.contains('Akan Buka')]),
        'sudah_tutup': len(df[df['status'].str.contains('Sudah Tutup')]),
        'last_update': datetime.now().isoformat()
    }
    
    with open('/opt/airflow/data/stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Timeline berhasil diproses: {stats}")


scrape_task = PythonOperator(
    task_id='scrape_beasiswa',
    python_callable=scrape_beasiswa_data,
    dag=dag,
)

process_task = PythonOperator(
    task_id='process_timeline',
    python_callable=process_timeline,
    dag=dag,
)

scrape_task >> process_task
