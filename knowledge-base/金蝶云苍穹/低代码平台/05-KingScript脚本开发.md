# 低代码开发平台 - KingScript脚本开发

> 文档来源: 金蝶云社区 - 开发平台专题
> 专题ID: 218022218066869248
> 整理时间: 2026-03-21

---

## 一、KingScript概述

### 1.1 什么是KingScript

KingScript是苍穹平台提供的脚本语言，用于实现业务逻辑的快速开发。它具有以下特点：

- **语法简洁**: 类似JavaScript的语法风格
- **类型安全**: 支持静态类型检查
- **易于学习**: 学习成本低，上手快
- **运行高效**: 编译执行，性能优秀

### 1.2 适用场景

| 场景 | 说明 |
|-----|------|
| 表单事件处理 | 字段变更、按钮点击等 |
| 操作脚本 | 单据操作前后处理 |
| 计算脚本 | 动态计算字段值 |
| 校验脚本 | 自定义数据校验 |
| 工作流脚本 | 流程处理逻辑 |

---

## 二、KingScript语法基础

### 2.1 基本语法

#### 变量声明
```javascript
// 变量声明
var name = "张三";
var age = 25;
var price = 99.9;
var isValid = true;

// 常量声明
const PI = 3.14159;
const MAX_COUNT = 100;
```

#### 条件判断
```javascript
// if语句
if (age > 18) {
    console.log("成年人");
} else if (age > 12) {
    console.log("青少年");
} else {
    console.log("儿童");
}

// 三元表达式
var status = age >= 18 ? "成年" : "未成年";
```

#### 循环
```javascript
// for循环
for (var i = 0; i < 10; i++) {
    console.log(i);
}

// while循环
var j = 0;
while (j < 10) {
    console.log(j);
    j++;
}

// 遍历数组
var items = [1, 2, 3, 4, 5];
for (var item in items) {
    console.log(item);
}
```

### 2.2 数据类型

| 类型 | 说明 | 示例 |
|-----|------|------|
| String | 字符串 | "Hello" |
| Number | 数值 | 123, 3.14 |
| Boolean | 布尔 | true, false |
| Date | 日期 | new Date() |
| Array | 数组 | [1, 2, 3] |
| Object | 对象 | {name: "张三"} |
| BigDecimal | 高精度数值 | BigDecimal("123.45") |

### 2.3 函数定义

```javascript
// 普通函数
function add(a, b) {
    return a + b;
}

// 带默认参数的函数
function greet(name, greeting = "你好") {
    return greeting + ", " + name + "!";
}

// 箭头函数
var multiply = (a, b) => a * b;

// 调用函数
var sum = add(1, 2);        // 3
var message = greet("张三"); // 你好, 张三!
var product = multiply(3, 4); // 12
```

### 2.4 类定义

```javascript
// 定义类
class Person {
    // 构造函数
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }
    
    // 方法
    sayHello() {
        return "你好，我是" + this.name;
    }
    
    // getter
    get info() {
        return this.name + "(" + this.age + "岁)";
    }
    
    // setter
    set personAge(age) {
        if (age > 0) {
            this.age = age;
        }
    }
}

// 继承
class Student extends Person {
    constructor(name, age, grade) {
        super(name, age);
        this.grade = grade;
    }
    
    study() {
        return this.name + "正在学习";
    }
}

// 使用类
var person = new Person("张三", 25);
console.log(person.sayHello());
console.log(person.info);
```

---

## 三、表单插件脚本开发

### 3.1 表单插件基础

```javascript
// 表单插件模板
plugin {
    // 插件初始化
    onInit() {
        console.log("插件初始化");
    }
    
    // 数据绑定后
    afterBindData() {
        // 初始化处理
        var status = this.getModel().getValue("status");
        this.handleStatusChange(status);
    }
    
    // 字段值变更
    propertyChanged(fieldName, newValue, oldValue) {
        if (fieldName === "qty" || fieldName === "price") {
            this.calculateAmount();
        }
    }
    
    // 按钮点击
    click(buttonKey) {
        if (buttonKey === "btn_submit") {
            this.handleSubmit();
        }
    }
    
    // 计算金额
    calculateAmount() {
        var qty = this.getModel().getValue("qty") || 0;
        var price = this.getModel().getValue("price") || 0;
        var amount = qty * price;
        this.getModel().setValue("amount", amount);
    }
    
    // 处理提交
    handleSubmit() {
        // 校验数据
        if (!this.validateData()) {
            return;
        }
        
        // 执行提交
        this.getView().showSuccessNotification("提交成功");
    }
    
    // 数据校验
    validateData() {
        var qty = this.getModel().getValue("qty");
        if (!qty || qty <= 0) {
            this.getView().showErrorNotification("数量必须大于0");
            return false;
        }
        return true;
    }
    
    // 处理状态变更
    handleStatusChange(status) {
        if (status === "approved") {
            this.getView().setReadOnly(true);
        }
    }
}
```

### 3.2 常用API

#### 视图API (View)
```javascript
// 显示消息
this.getView().showMessage("提示信息");
this.getView().showSuccessNotification("成功");
this.getView().showErrorNotification("错误");
this.getView().showWarningNotification("警告");

// 控件可见性
this.getView().setVisible("fieldname", true/false);
this.getView().setReadOnly("fieldname", true/false);
this.getView().setEnabled("fieldname", true/false);

// 页面操作
this.getView().close();                    // 关闭页面
this.getView().refresh();                  // 刷新页面
this.getView().invokeOperation("save");    // 执行操作
```

#### 数据模型API (Model)
```javascript
// 获取/设置字段值
var value = this.getModel().getValue("fieldname");
this.getModel().setValue("fieldname", value);

// 获取整个数据对象
var data = this.getModel().getDataEntity();

// 分录操作
this.getModel().addRow("entryentity");                     // 新增行
this.getModel().deleteRow("entryentity", rowIndex);        // 删除行
var rowCount = this.getModel().getEntryRowCount("entry");  // 获取行数
var rowData = this.getModel().getEntryRowValue("entry", rowIndex); // 获取行数据
```

---

## 四、操作插件脚本开发

### 4.1 操作插件模板

```javascript
operation {
    // 操作执行前校验
    beforeExecute(args) {
        var data = this.getModel().getDataEntity();
        
        // 校验逻辑
        if (data.amount <= 0) {
            this.addErrorMessage("金额必须大于0");
            return false;
        }
        
        return true;
    }
    
    // 操作执行中
    execute(args) {
        var data = this.getModel().getDataEntity();
        
        // 处理逻辑
        data.processTime = new Date();
        
        return true;
    }
    
    // 操作执行后
    afterExecute(result) {
        if (result.success) {
            this.getView().showSuccessNotification("操作成功");
        }
    }
}
```

---

## 五、单据转换脚本开发

### 5.1 转换插件模板

```javascript
convert {
    // 数据转换前
    beforeConvert(sourceBills) {
        // 预处理源单据
        for (var bill in sourceBills) {
            bill.convertFlag = true;
        }
    }
    
    // 字段映射后
    afterFieldMapping(targetBill, sourceBill) {
        // 自定义映射逻辑
        targetBill.sourceBillNo = sourceBill.billNo;
        targetBill.convertDate = new Date();
        
        // 处理分录
        var sourceEntry = sourceBill.entry;
        var targetEntry = [];
        
        for (var row in sourceEntry) {
            var newRow = {
                material: row.material,
                qty: row.qty,
                price: row.price,
                amount: row.qty * row.price
            };
            targetEntry.push(newRow);
        }
        
        targetBill.entry = targetEntry;
    }
    
    // 转换完成后
    afterConvert(targetBills) {
        // 后处理逻辑
    }
}
```

---

## 六、工作流脚本开发

### 6.1 工作流插件模板

```javascript
workflow {
    // 计算审批人
    calcApprovers(args) {
        var data = this.getModel().getDataEntity();
        var amount = data.amount;
        
        var approvers = [];
        
        if (amount > 100000) {
            // 大额需要总经理审批
            approvers.push("general_manager");
        } else if (amount > 10000) {
            // 中额需要部门经理审批
            approvers.push("dept_manager");
        } else {
            // 小额只需要主管审批
            approvers.push("supervisor");
        }
        
        return approvers;
    }
    
    // 流程条件判断
    checkCondition(condition) {
        var data = this.getModel().getDataEntity();
        
        if (condition === "need_finance_review") {
            return data.amount > 50000;
        }
        
        return false;
    }
    
    // 审批通知
    notify(args) {
        var data = this.getModel().getDataEntity();
        var message = "单据【" + data.billNo + "】需要您审批";
        
        // 发送通知
        this.sendNotification(args.approver, message);
    }
}
```

---

## 七、报表脚本开发

### 7.1 报表取数脚本

```javascript
report {
    // 查询数据
    query(args) {
        var filter = args.filter;
        var startDate = filter.startDate;
        var endDate = filter.endDate;
        
        // 构建查询条件
        var conditions = [];
        if (startDate) {
            conditions.push("date >= '" + startDate + "'");
        }
        if (endDate) {
            conditions.push("date <= '" + endDate + "'");
        }
        
        // 执行查询
        var sql = "SELECT * FROM sales_order WHERE " + conditions.join(" AND ");
        var result = this.query(sql);
        
        return result;
    }
    
    // 处理数据
    processData(data) {
        var result = [];
        var groupMap = {};
        
        // 分组汇总
        for (var row in data) {
            var key = row.customerId;
            if (!groupMap[key]) {
                groupMap[key] = {
                    customerName: row.customerName,
                    totalAmount: 0,
                    orderCount: 0
                };
            }
            groupMap[key].totalAmount += row.amount;
            groupMap[key].orderCount += 1;
        }
        
        // 转换为数组
        for (var key in groupMap) {
            result.push(groupMap[key]);
        }
        
        return result;
    }
}
```

---

## 八、调试与测试

### 8.1 调试方法

```javascript
// 使用console.log调试
console.log("调试信息: ", value);
console.log("对象信息: ", JSON.stringify(obj));

// 使用断点调试
debugger;

// 使用try-catch捕获异常
try {
    // 可能出错的代码
    var result = riskyOperation();
} catch (e) {
    console.error("错误: ", e);
    this.getView().showErrorNotification("操作失败: " + e.message);
}
```

### 8.2 单元测试

```javascript
test {
    // 测试计算金额
    testCalculateAmount() {
        // 准备测试数据
        this.getModel().setValue("qty", 10);
        this.getModel().setValue("price", 100);
        
        // 执行计算
        this.calculateAmount();
        
        // 验证结果
        var amount = this.getModel().getValue("amount");
        assert(amount === 1000, "金额计算错误");
    }
}
```

---

## 九、最佳实践

### 9.1 编码规范

1. **命名规范**
   - 变量/函数: 驼峰命名 (calculateAmount)
   - 常量: 全大写下划线 (MAX_COUNT)
   - 类: 帕斯卡命名 (PersonInfo)

2. **注释规范**
```javascript
/**
 * 计算金额
 * @param {Number} qty - 数量
 * @param {Number} price - 单价
 * @returns {Number} 金额
 */
function calculateAmount(qty, price) {
    return qty * price;
}
```

3. **异常处理**
```javascript
try {
    // 业务逻辑
} catch (e) {
    console.error("错误详情: ", e);
    this.getView().showErrorNotification("操作失败，请联系管理员");
}
```

### 9.2 性能优化

1. **减少DOM操作**: 批量更新数据
2. **使用缓存**: 缓存频繁访问的数据
3. **异步处理**: 耗时操作使用异步

---

## 十、常见问题

**Q: 脚本中如何调用Java类？**
```javascript
var StringUtils = Java.type("kd.bos.util.StringUtils");
var result = StringUtils.isEmpty(value);
```

**Q: 如何处理日期？**
```javascript
var date = new Date();
var formattedDate = date.format("yyyy-MM-dd");
```

**Q: 如何进行数值计算？**
```javascript
var BigDecimal = Java.type("java.math.BigDecimal");
var a = new BigDecimal("10.5");
var b = new BigDecimal("20.3");
var result = a.add(b); // 加法
```

---

**更新时间**: 2026-03-21
**维护者**: 礼部
