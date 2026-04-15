'''
売上データから各種形式のレポートを生成するプログラム

このプログラムは、JSON形式の売上データを読み込み、
CSV、テキスト、JSON形式のレポートファイルを生成します。
各レポートには統計情報（合計、平均、最大、最小）が含まれます。
'''

import json
import csv
import os 
import datetime

def load_report_file(filename):
    """
    JSONファイルから売上データを読み込む        
    Returns:
        list or None: 売上データのリスト。エラー時はNone
    """    
    base_file = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_file,filename)
    try:
        with open(filepath,'r',encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ ファイル '{filename}' を正常に読み込みました。")
        return data
     
    except FileNotFoundError:
        print(f"❌ エラー：ファイル '{filename}' が見つかりません。")
        return None
    except json.JSONDecodeError:
        print(f"❌ エラー：ファイル '{filename}' の内容がJSON形式ではありません。")
        return None
    except Exception as e:
        print(f"❌ エラー：ファイル読み込み中に予期せぬエラーが発生しました。{e}")
        return None

class ReportGenerator:
    """
    売上データからレポートを生成するクラス
    
    Attributes:
        data (list): 売上データのリスト
        report_text (str): テキストレポートの内容
        created_at (str): レポート作成日時
        statistics (dict): 統計情報（合計、平均、最大、最小）
    """

    def __init__(self,data):
        self.data = data
        self.report_text = None
        self.created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.statistics = None
        print("✅ ReportGeneratorの準備ができました。")

    def _is_safe_to_process(self):
        # データが処理可能な状態かチェック
        if not self.data:
            print("❌ エラー:処理すべきデータがありません。")      
            return False
        
        for i,item in enumerate(self.data, 1):
            name = item.get('name')
            sales = item.get('sales')
            if name is None or not isinstance(sales,(int,float)):
                print(f"エラー: {i}番目のデータ '{name}'または'{sales}' の形式が正しくありません。")
                return False     
        return True
    
    def _make_header(self):
        header = [
            "--- 月次売上レポート ---",
            f"作成日時: {self.created_at}", 
            "-----------------------",
            "No. | 担当者 | 売上 (円)",
            "-----------------------"
        ]
        return "\n".join(header)
    
    def _calculate_statistics(self):
        # 統計情報を計算して保存
        if not self._is_safe_to_process():
            return None
        
        sales_values = [item['sales'] for item in self.data]

        # 空リストチェック（念のため）
        if not sales_values:
            self.statistics = {
                'total_sales':0,
                'average_sales':0.0,
                'max_sales':0,
                'min_sales':0
            }
            return self.statistics
        
        total_sales = sum(sales_values)

        self.statistics = {
            'total_sales': total_sales,
            'average_sales': total_sales / len(sales_values),
            'max_sales': max(sales_values),
            'min_sales':min(sales_values)
        }
        return self.statistics
    
    def process_data(self):
        # 売上データを処理してテキストレポートを生成
        if not self._is_safe_to_process():
            return
        
        #統計情報を計算 
        if self.statistics is None:
            self._calculate_statistics()

        report_lines = [self._make_header()]

        for i, item in enumerate(self.data, 1): #インデックスは1から開始
            line = f"{i:3} | {item['name']:^6} | {item['sales']:>8,}"
            report_lines.append(line)

        report_lines.append("-----------------------")
        report_lines.append(f"合計売上: ¥{self.statistics['total_sales']:,.0f} 円")
        report_lines.append(f"平均売上: ¥{self.statistics['average_sales']:,.2f} 円")
        report_lines.append(f"最大売上: ¥{self.statistics['max_sales']:>,} 円")
        report_lines.append(f"最小売上: ¥{self.statistics['min_sales']:>,} 円")

        self.report_text = "\n".join(report_lines)

    def generate_csv_report(self, filename):
        #各メソッドで毎回チェックすることは必須
        #csv,json,txtの分岐を作ったなら分岐にそれぞれチェックと再利用するためのコードを書く
        if not self._is_safe_to_process():
            return
        
        #他のメソッドで処理されていればその処理データを使う
        if self.statistics is None:
            self._calculate_statistics()
        
        fieldnames = ['No.','担当者','売上']

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(fieldnames)

                for i, item in enumerate(self.data, 1): # 1から開始
                    writer.writerow([
                        i,
                        item['name'],
                        item['sales']
                    ])

                writer.writerow([])
                writer.writerow([f"合計売上: ¥{self.statistics['total_sales']:,.0f} 円"])
                writer.writerow([f"平均売上: ¥{self.statistics['average_sales']:,.2f} 円"])
                writer.writerow([f"最大売上: ¥{self.statistics['max_sales']:>,} 円"])
                writer.writerow([f"最小売上: ¥{self.statistics['min_sales']:>,} 円"])
            
            print(f"✅ レポートをCSVファイル: {filename} に書き込みました。")

        except PermissionError: # ファイル開きっぱ
            print("ファイルを閉じてください")
        except OSError as e: # ファイル名変えてる
            print(f"OSエラー: {e}")
        except Exception as e: # {type(e).__name__} はエラーの種類と名前を検索し名前だけ持ってくる
            print(f"エラー: {e}")
            print(f"種類; {type(e).__name__}")

    def generate_text_report(self,filename):
        if self.report_text is None: # テキストでは整形済みのデータが欲しい
            self.process_data()

        if self.report_text is None: # process_data()でエラーが発生した場合
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.report_text)
            print(f"✅ レポートをTEXTファイル: {filename} に書き込みました。")

        except PermissionError:
            print("ファイルを閉じてください")
        except OSError as e:
            print(f"OSエラー: {e}")
        except Exception as e:
            print(f"エラー: {e}")
            print(f"種類; {type(e).__name__}") 

    def generate_json_report(self, filename):
        if not self._is_safe_to_process(): 
            return
        
        if self.statistics is None:
            self._calculate_statistics()

        output_bundle = {
            "metadata": {
                "created_at": self.created_at,
                "total_count": len(self.data),
                "total_sales": self.statistics['total_sales'],
                "average_sales": round(self.statistics['average_sales'], 2),
                "max_sales": self.statistics['max_sales'],
                "min_sales": self.statistics['min_sales']
            },
            "details": self.data
        }

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_bundle, f, ensure_ascii=False, indent=4)
            print(f"✅ レポートをJSONファイル: {filename} に書き込みました。")

        except PermissionError:
            print("ファイルを閉じてください")
        except OSError as e:
            print(f"OSエラー: {e}")
        except Exception as e:
            print(f"エラー: {e}")
            print(f"種類; {type(e).__name__}")

if __name__ == "__main__" :
    input_file = "L2-04_sales_data.json"
    load_data = load_report_file(input_file)

    if load_data:
        generator = ReportGenerator(load_data)
        # 最初以降のファイル作成は保存データ(self.)を呼び出す仕組みがクラス。
        generator.generate_json_report("L2-04_class_sales_report_02.json")
        generator.generate_csv_report("L2-04_class_sales_report_02.csv")
        generator.generate_text_report("L2-04_class_sales_report_02.txt")