"""
이메일 알림 시스템
경제 이벤트를 이메일로 전송
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List
import logging
import os

class EmailNotifier:
    """이메일 알림 전송 클래스"""
    
    def __init__(self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.logger = logging.getLogger(__name__)
        
        # 이메일 설정 (환경변수에서 로드)
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")  # 앱 비밀번호 사용
        self.recipient_email = os.getenv("RECIPIENT_EMAIL")
    
    def send_market_summary_email(self, monitoring_result: Dict) -> bool:
        """시장 요약 이메일 전송"""
        try:
            subject = f"📊 경제 시장 분석 요약 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # HTML 이메일 내용 생성
            html_content = self._create_market_summary_html(monitoring_result)
            
            return self._send_email(subject, html_content)
            
        except Exception as e:
            self.logger.error(f"시장 요약 이메일 전송 실패: {str(e)}")
            return False
    
    def send_critical_alert_email(self, alert_data: Dict) -> bool:
        """긴급 알림 이메일 전송"""
        try:
            subject = f"🚨 긴급 경제 알림: {alert_data['symbol']} - {alert_data.get('event_type', 'Alert')}"
            
            html_content = self._create_critical_alert_html(alert_data)
            
            return self._send_email(subject, html_content)
            
        except Exception as e:
            self.logger.error(f"긴급 알림 이메일 전송 실패: {str(e)}")
            return False
    
    def _create_market_summary_html(self, monitoring_result: Dict) -> str:
        """시장 요약 HTML 생성"""
        risk_level = monitoring_result['risk_assessment']['overall_risk_level']
        risk_colors = {
            "low": "#28a745",
            "medium": "#ffc107", 
            "high": "#fd7e14",
            "very_high": "#dc3545"
        }
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%); color: white; padding: 20px; text-align: center;">
                <h1>📊 경제 시장 분석 요약</h1>
                <p>{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</p>
            </div>
            
            <div style="padding: 20px;">
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="color: {risk_colors.get(risk_level, '#333')};">
                        위험도: {risk_level.upper().replace('_', ' ')}
                    </h2>
                    <p><strong>위험 점수:</strong> {monitoring_result['risk_assessment']['risk_score']:.2f}/1.00</p>
                    <p><strong>감지된 이벤트:</strong> {monitoring_result['total_events']}개</p>
                </div>
                
                <h3>🚨 주요 알림</h3>
                <ul>
        """
        
        for alert in monitoring_result.get('priority_alerts', [])[:5]:
            html += f"""
                <li style="margin-bottom: 10px;">
                    <strong>[{alert['symbol']}]</strong> {alert['message']}
                    <br><small>심각도: {alert['severity']:.2f}</small>
                </li>
            """
        
        html += """
                </ul>
                
                <div style="background: #e7f3ff; padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <h3>💡 주요 인사이트</h3>
                    <ul>
        """
        
        insights = monitoring_result.get('advanced_analysis', {}).get('analysis_summary', {}).get('key_insights', [])
        for insight in insights:
            html += f"<li>{insight}</li>"
        
        html += """
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 30px; color: #666; font-size: 0.9em;">
                    <p>본 리포트는 AI가 실시간 시장 데이터를 분석하여 자동 생성한 것입니다.</p>
                    <p>투자 결정 시 추가적인 분석과 전문가 상담을 권장합니다.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_critical_alert_html(self, alert_data: Dict) -> str:
        """긴급 알림 HTML 생성"""
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #dc3545; color: white; padding: 20px; text-align: center;">
                <h1>🚨 긴급 경제 알림</h1>
                <h2>{alert_data['symbol']}</h2>
            </div>
            
            <div style="padding: 20px;">
                <div style="background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h3>{alert_data.get('message', '긴급 이벤트 발생')}</h3>
                    <p><strong>심각도:</strong> {alert_data.get('severity', 0):.2f}/1.00</p>
                    <p><strong>발생 시간:</strong> {alert_data.get('timestamp', datetime.now().isoformat())}</p>
                </div>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 8px;">
                    <h3>📊 상세 정보</h3>
                    <p><strong>현재가:</strong> {alert_data.get('current_price', 'N/A')}</p>
                    <p><strong>변화율:</strong> {alert_data.get('change_percent', 'N/A')}%</p>
                    <p><strong>거래량:</strong> {alert_data.get('volume', 'N/A'):,}</p>
                </div>
                
                <div style="text-align: center; margin-top: 30px; color: #666; font-size: 0.9em;">
                    <p>즉시 확인이 필요한 중요한 시장 변화입니다.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _send_email(self, subject: str, html_content: str) -> bool:
        """이메일 전송"""
        try:
            if not all([self.sender_email, self.sender_password, self.recipient_email]):
                self.logger.error("이메일 설정이 완료되지 않았습니다.")
                return False
            
            # 메시지 생성
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = self.recipient_email
            
            # HTML 파트 추가
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)
            
            # SMTP 서버 연결 및 전송
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, message.as_string())
            
            self.logger.info(f"이메일 전송 성공: {subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"이메일 전송 실패: {str(e)}")
            return False

# 사용 예시
def setup_email_notifications():
    """이메일 알림 설정 예시"""
    print("📧 이메일 알림 설정 가이드")
    print("=" * 40)
    print("1. Gmail 앱 비밀번호 생성:")
    print("   - Google 계정 → 보안 → 2단계 인증 활성화")
    print("   - 앱 비밀번호 생성")
    print()
    print("2. 환경변수 설정:")
    print("   export SENDER_EMAIL='your-email@gmail.com'")
    print("   export SENDER_PASSWORD='your-app-password'")
    print("   export RECIPIENT_EMAIL='recipient@email.com'")
    print()
    print("3. 테스트 실행:")
    print("   python notifications/email_notifier.py")

if __name__ == "__main__":
    setup_email_notifications()
