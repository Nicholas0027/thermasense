# file: server/app/hvac_controller.py
from decimal import Decimal

class AbstractHVACController:
    """
    定义所有HVAC控制器都必须遵守的“标准接口” (抽象基类)。
    它规定，任何一个控制器都必须提供一个名为 set_temperature 的方法。
    """
    def set_temperature(self, zone_id: str, temperature: Decimal):
        # 这个 pass 语句意味着基类本身不做任何具体操作。
        # 具体的实现将由它的子类来完成。
        raise NotImplementedError("每个控制器子类都必须实现set_temperature方法!")

class DummyHVACController(AbstractHVACController):
    """
    一个“模拟”的HVAC控制器，用于开发和测试。
    它不与任何真实硬件交互，只是在控制台打印出将要执行的操作。
    这让我们可以在没有真实硬件的情况下，完整地测试整个软件逻辑。
    """
    def set_temperature(self, zone_id: str, temperature: Decimal):
        """
        模拟设置指定分区的温度。
        """
        print("======================================================")
        print(f"**[HVAC模拟器]** 收到指令: 正在尝试将分区 '{zone_id}' 的温度设置为 {temperature}°C")
        print(">> 在真实世界中，这里的代码将会是调用具体硬件的API。")
        print("======================================================")

# --- 未来扩展区 ---
# class EnlightedHVACController(AbstractHVACController):
#     def set_temperature(self, zone_id: str, temperature: Decimal):
#         # 这里将包含调用Enlighted系统API的真实代码
#         # import requests
#         # url = f"https://api.enlightedinc.com/zones/{zone_id}/setpoint"
#         # headers = {"Authorization": "Bearer YOUR_API_KEY"}
#         # data = {"temperature": temperature}
#         # response = requests.post(url, headers=headers, json=data)
#         # ... 处理响应 ...
#         pass

# --- 当前使用的控制器 ---
# 我们在这里决定当前系统使用哪个“转换插头”。
# 现在我们使用模拟控制器，未来有了真实接口后，只需将这一行切换即可。
current_controller = DummyHVACController()

# --- 统一的调用入口 ---
def set_zone_temperature(zone_id: str, temperature: Decimal):
    """
    这是系统中唯一用来调用温度设置功能的函数。
    它会自动使用我们当前配置的控制器实例。
    """
    current_controller.set_temperature(zone_id, temperature)
