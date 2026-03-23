#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉工作通知发送器
=====================================
发送消息到钉钉"工作通知"，而不是私聊
"""

import json
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional


class DingTalkWorkNotice:
    """钉钉工作通知发送器"""
    
    def __init__(self, config_path: str = "/root/.openclaw/openclaw.json"):
        """初始化"""
        self.config = self._load_config(config_path)
        self.account = self.config['channels']['dingtalk']['accounts']['default']
        
        self.client_id = self.account['clientId']
        self.client_secret = self.account['clientSecret']
        self.agent_id = self.account['agentId']
        self.corp_id = self.account['corpId']
        self.user_phone = self.account['userPhone']
        
        self.access_token = None
        
    def _load_config(self, config_path: str) -> dict:
        """加载配置"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _http_get(self, url: str, params: dict = None, timeout: int = 10) -> dict:
        """HTTP GET请求"""
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode('utf-8'))
    
    def _http_post(self, url: str, data: dict, timeout: int = 10) -> dict:
        """HTTP POST请求"""
        headers = {'Content-Type': 'application/json'}
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode('utf-8'))
    
    def get_access_token(self) -> str:
        """获取access_token"""
        url = "https://oapi.dingtalk.com/gettoken"
        params = {
            'appkey': self.client_id,
            'appsecret': self.client_secret
        }
        
        result = self._http_get(url, params)
        
        if result.get('errcode') == 0:
            self.access_token = result['access_token']
            return self.access_token
        else:
            raise Exception(f"获取access_token失败: {result}")
    
    def get_user_id_by_phone(self, phone: str) -> str:
        """通过手机号获取userId"""
        if not self.access_token:
            self.get_access_token()
        
        url = f"https://oapi.dingtalk.com/topapi/v2/user/getbymobile?access_token={self.access_token}"
        data = {'mobile': phone}
        
        result = self._http_post(url, data)
        
        if result.get('errcode') == 0:
            return result['result']['userid']
        else:
            raise Exception(f"获取userId失败: {result}")
    
    def send_work_notice(self, message: str, user_id: Optional[str] = None) -> dict:
        """
        发送工作通知
        
        Args:
            message: 消息内容
            user_id: 用户ID（可选，默认使用配置中的手机号）
        
        Returns:
            发送结果
        """
        if not self.access_token:
            self.get_access_token()
        
        if not user_id:
            # 直接使用手机号作为userId（钉钉支持）
            user_id = self.user_phone
        
        url = f"https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?access_token={self.access_token}"
        
        data = {
            "agent_id": self.agent_id,
            "userid_list": user_id,
            "msg": {
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
        }
        
        result = self._http_post(url, data)
        return result
    
    def send_markdown_work_notice(self, title: str, content: str, user_id: Optional[str] = None) -> dict:
        """
        发送Markdown工作通知
        
        Args:
            title: 标题
            content: Markdown内容
            user_id: 用户ID（可选）
        
        Returns:
            发送结果
        """
        if not self.access_token:
            self.get_access_token()
        
        if not user_id:
            user_id = self.get_user_id_by_phone(self.user_phone)
        
        url = f"https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?access_token={self.access_token}"
        
        data = {
            "agent_id": self.agent_id,
            "userid_list": user_id,
            "msg": {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": content
                }
            }
        }
        
        result = self._http_post(url, data)
        return result


def send_work_notice(message: str) -> dict:
    """
    快速发送工作通知（全局函数）
    
    Args:
        message: 消息内容
    
    Returns:
        发送结果
    """
    sender = DingTalkWorkNotice()
    return sender.send_work_notice(message)


def send_markdown_work_notice(title: str, content: str) -> dict:
    """
    快速发送Markdown工作通知（全局函数）
    
    Args:
        title: 标题
        content: Markdown内容
    
    Returns:
        发送结果
    """
    sender = DingTalkWorkNotice()
    return sender.send_markdown_work_notice(title, content)


if __name__ == '__main__':
    # 测试发送
    print("="*70)
    print("测试钉钉工作通知发送")
    print("="*70)
    
    sender = DingTalkWorkNotice()
    
    print("\n【1. 获取access_token】")
    token = sender.get_access_token()
    print(f"✅ access_token: {token[:20]}...")
    
    print("\n【2. 获取userId】")
    user_id = sender.get_user_id_by_phone(sender.user_phone)
    print(f"✅ userId: {user_id}")
    
    print("\n【3. 发送工作通知】")
    result = sender.send_work_notice("🔔 测试工作通知 - 这是一条工作通知消息")
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if result.get('errcode') == 0:
        print("\n✅ 工作通知发送成功！")
        print("   请在钉钉 → 工作通知 中查看")
    else:
        print(f"\n❌ 发送失败: {result.get('errmsg')}")
