# file: server/app/init_db.py
from .database import SessionLocal, engine
from . import models

# ✅ 定义期望存在的所有分区（英文ID + 中文名 + 初始温度）
DESIRED_ZONES = [
    {
        "id": "office_a",
        "name": "办公室A区",
        "temp": 24.5
    },
    {
        "id": "library_b",
        "name": "图书馆B区",
        "temp": 26.0
    },
    {
        "id": "classroom_a",
        "name": "教室A",
        "temp": 22.0
    },
    {
        "id": "studio_e",
        "name": "录音室E",
        "temp": 25.0
    }
]

def init_db():
    # 创建所有表（如果尚未存在）
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 获取所有已存在的 zone_id
        existing_zone_ids = {
            zone.zone_id: zone
            for zone in db.query(models.Zone).all()
        }

        updated = 0
        created = 0

        for zone_data in DESIRED_ZONES:
            zone_id = zone_data['id']
            name = zone_data['name']
            temp = zone_data['temp']

            if zone_id in existing_zone_ids:
                zone = existing_zone_ids[zone_id]
                # 若中文名不同，则更新
                if zone.name != name:
                    print(f"📝 更新 zone {zone_id}: 名称由 '{zone.name}' → '{name}'")
                    zone.name = name
                    updated += 1
            else:
                # 插入新分区
                new_zone = models.Zone(
                    zone_id=zone_id,
                    name=name,
                    current_temp=temp,
                    recommended_temp=temp
                )
                db.add(new_zone)
                print(f"➕ 添加新分区: {zone_id} - {name}")
                created += 1

        if created or updated:
            db.commit()
            print(f"✅ 已更新数据库: 新增 {created} 个分区，修改 {updated} 个名称")
        else:
            print("ℹ️ 数据库已是最新，无需更改")

    finally:
        db.close()

if __name__ == "__main__":
    init_db()
