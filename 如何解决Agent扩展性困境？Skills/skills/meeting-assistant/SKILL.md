---
name: meeting-assistant
description: 将会议记录整理为结构化会议纪要，提炼关键结论、决策和Todo项。
---

# 会议助手

## Instructions
会议助手按以下步骤执行：

### Step 1：内容理解
- 按发言人或话题理解并划分内容

### Step 2：识别关键信息
- 会议主题
- 核心讨论点
- 分歧与共识

### Step 3：提炼决策
- 明确哪些是已达成的结论

### Step 4：提取Todo项
- 谁（Owner）
- 做什么（Task）
- 截止时间（Deadline）

### Step 5：结构化输出
- 使用会议纪要模板中的结构输出，参考：assets/meeting-template.md

### Step 6: 差旅申请
- 如果会议中提到差旅，请读取部门关于差旅费用说明手册：references/travel_policy.md ，评估差旅预算；
- 发起差旅申请并审批，运行 scripts/travel_approve.py 发起申请。使用方法如下：
```python
python3 scripts/travel_approve.py "${name}" "${amount}" "${reason}"
```

## 约束条件
- 不允许逐字复述会议内容；
- 必须区分『讨论』和『决策』；
- Todo必须明确Owner；
- 会议纪要中涉及的时间必须使用绝对时间。