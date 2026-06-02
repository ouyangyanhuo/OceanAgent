"""海洋数据类型别名。

Mock 海洋数据目前保持灵活 dict 结构，后续接真实数据源时可替换成严格模型。
"""

from typing import Any

# 单条海洋观测/浮标/海流/渔场/航线记录。
OceanRecord = dict[str, Any]
