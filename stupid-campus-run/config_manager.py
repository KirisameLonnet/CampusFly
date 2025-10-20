#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校园跑程序 - 配置管理工具
"""

import json
import os
import sys

def load_config():
    """加载配置文件"""
    config_file = "user_config.json"
    default_config = {
        "last_username": "",
        "last_password": "",
        "last_school": "上海大学",
        "last_distance": 5000,
        "remember_credentials": False
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合并默认配置
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            return default_config
    else:
        return default_config

def save_config(config):
    """保存配置文件"""
    try:
        with open("user_config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print("✅ 配置已保存")
        return True
    except Exception as e:
        print(f"❌ 保存配置文件失败: {e}")
        return False

def show_config(config):
    """显示当前配置"""
    print("📋 当前配置:")
    print(f"  用户名: {config.get('last_username', '未设置')}")
    print(f"  密码: {'已保存（加密）' if config.get('last_password') else '未保存'}")
    print(f"  学校: {config.get('last_school', '未设置')}")
    print(f"  距离: {config.get('last_distance', '未设置')}米")
    print(f"  记住凭据: {'是' if config.get('remember_credentials', False) else '否'}")

def clear_config():
    """清空配置"""
    config = {
        "last_username": "",
        "last_school": "上海大学",
        "last_distance": 5000,
        "remember_credentials": False
    }
    if save_config(config):
        print("✅ 配置已清空")

def main():
    """主函数"""
    print("🔧 校园跑程序配置管理工具")
    print("=" * 40)
    
    config = load_config()
    
    while True:
        print("\n请选择操作:")
        print("1. 查看当前配置")
        print("2. 修改用户名")
        print("3. 修改密码")
        print("4. 修改学校")
        print("5. 修改距离")
        print("6. 清空配置")
        print("7. 退出")
        
        choice = input("\n请输入选项编号 (1-7): ").strip()
        
        if choice == "1":
            show_config(config)
            
        elif choice == "2":
            username = input("请输入新的用户名（手机号）: ").strip()
            if username:
                config["last_username"] = username
                save_config(config)
            else:
                print("❌ 用户名不能为空")
                
        elif choice == "3":
            password = input("请输入新的密码: ").strip()
            if password:
                # 这里需要加密密码，但配置管理工具没有加密功能
                # 建议用户使用主程序来设置密码
                print("⚠️ 密码管理功能需要在主程序中设置")
                print("请运行 python tui.py 来设置密码")
            else:
                print("❌ 密码不能为空")
                
        elif choice == "4":
            print("请选择学校:")
            print("1. 上海大学")
            print("2. 上海中医药大学")
            school_choice = input("请输入学校编号: ").strip()
            if school_choice == "1":
                config["last_school"] = "上海大学"
                save_config(config)
            elif school_choice == "2":
                config["last_school"] = "上海中医药大学"
                save_config(config)
            else:
                print("❌ 无效选择")
                
        elif choice == "5":
            try:
                distance = int(input("请输入新的距离（米）: ").strip())
                if 100 <= distance <= 20000:
                    config["last_distance"] = distance
                    save_config(config)
                else:
                    print("❌ 距离必须在100-20000米之间")
            except ValueError:
                print("❌ 请输入有效的数字")
                
        elif choice == "6":
            confirm = input("确认清空所有配置? (y/n): ").strip().lower()
            if confirm == 'y':
                clear_config()
            else:
                print("❌ 操作已取消")
                
        elif choice == "7":
            print("👋 再见!")
            break
            
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main()
