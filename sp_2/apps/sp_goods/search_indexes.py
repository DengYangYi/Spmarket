# 导入全文检索框架索引类
from haystack import indexes
from sp_goods.models import GoodsSKU


class GoodsSKUSearchIndex(indexes.SearchIndex, indexes.Indexable):
	# 设置需要检索的主要字段内容 use_template表示字段内容在模板中
	# 设置用于建立所以你的字段 字段定义在模板里面
	text = indexes.CharField(document=True, use_template=True)

	# 获取检索对应对的模型
	def get_model(self):
		return GoodsSKU

	# 设置检索需要使用的查询集
	def index_queryset(self, using=None):
		"""Used when the entire index for model is updated."""
		return self.get_model().objects.all()
