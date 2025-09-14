import tempfile

def create_tmp_sql_file(sql_content) -> str:
    tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8')
    tmp_file.write(sql_content)
    tmp_file.close()
    return tmp_file.name