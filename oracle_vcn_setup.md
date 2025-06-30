# Oracle Cloud VCN 설정 및 서비스 한도 해결 가이드

## 🚨 Service Limits Status 오류 해결

### 문제 원인
- Free Tier VCN 개수 한도 초과
- 서브넷 개수 제한
- IP 주소 범위 부족

### 해결 방법

#### 1. 기존 리소스 정리
```bash
# Oracle Cloud Console에서 확인
# - Compute → Instances (사용하지 않는 인스턴스 삭제)
# - Networking → VCN (사용하지 않는 VCN 삭제)
# - Storage → Block Volumes (사용하지 않는 볼륨 삭제)
```

#### 2. VCN 재사용 (권장)
기존 VCN이 있다면 새로운 서브넷 추가:

**VCN 설정:**
- **CIDR Block**: 10.0.0.0/16
- **DNS Resolution**: Enabled
- **DNS Hostnames**: Enabled

**서브넷 설정:**
- **Public Subnet**: 10.0.1.0/24
- **Private Subnet**: 10.0.2.0/24 (필요시)

#### 3. 보안 리스트 설정
```bash
# Ingress Rules
Source: 0.0.0.0/0, Port: 22 (SSH)
Source: 0.0.0.0/0, Port: 80 (HTTP)
Source: 0.0.0.0/0, Port: 443 (HTTPS)
Source: 0.0.0.0/0, Port: 8000 (API)
```

## 🔧 최적화된 VCN 구성

### Free Tier 권장 설정
```
VCN: 1개
├── Public Subnet: 1개 (10.0.1.0/24)
├── Private Subnet: 1개 (10.0.2.0/24) - 선택사항
├── Internet Gateway: 1개
├── Route Table: 1개
└── Security List: 1개
```

### 네트워크 구성 스크립트
```bash
#!/bin/bash
# vcn_setup.sh

echo "🔧 Oracle Cloud VCN 설정 중..."

# VCN 생성 (기존 VCN이 없는 경우)
VCN_ID=$(oci network vcn create \
  --compartment-id $COMPARTMENT_ID \
  --cidr-block "10.0.0.0/16" \
  --display-name "projectoldman-vcn" \
  --dns-label "projectoldman" \
  --query 'data.id' --raw-output)

echo "VCN ID: $VCN_ID"

# Internet Gateway 생성
IGW_ID=$(oci network internet-gateway create \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_ID \
  --display-name "projectoldman-igw" \
  --is-enabled true \
  --query 'data.id' --raw-output)

echo "Internet Gateway ID: $IGW_ID"

# Public Subnet 생성
SUBNET_ID=$(oci network subnet create \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_ID \
  --cidr-block "10.0.1.0/24" \
  --display-name "projectoldman-public-subnet" \
  --dns-label "public" \
  --security-list-ids '["'$SECURITY_LIST_ID'"]' \
  --query 'data.id' --raw-output)

echo "Subnet ID: $SUBNET_ID"
```

## 📊 서비스 한도 확인

### Free Tier 한도
- **VCN**: 1-3개
- **Subnet**: VCN당 2-6개
- **Compute Instances**: 2개
- **Block Storage**: 200GB
- **Object Storage**: 20GB

### 한도 확인 명령어
```bash
# OCI CLI로 한도 확인
oci limits resource-availability get \
  --compartment-id $COMPARTMENT_ID \
  --service-name "vcn" \
  --limit-name "vcn-count"

oci limits resource-availability get \
  --compartment-id $COMPARTMENT_ID \
  --service-name "subnet" \
  --limit-name "subnet-count"
```

## 🚀 대안 해결책

### 1. 기존 VCN 활용
```bash
# 기존 VCN ID 확인
oci network vcn list --compartment-id $COMPARTMENT_ID

# 기존 VCN에 서브넷 추가
oci network subnet create \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $EXISTING_VCN_ID \
  --cidr-block "10.0.3.0/24" \
  --display-name "projectoldman-subnet-2"
```

### 2. 리소스 정리 후 재시도
```bash
# 사용하지 않는 리소스 삭제
oci compute instance terminate --instance-id $INSTANCE_ID
oci network vcn delete --vcn-id $VCN_ID
oci network subnet delete --subnet-id $SUBNET_ID
```

### 3. Support 요청
- **Service Request** 생성
- 한도 증가 요청 (Free Tier에서는 제한적)
- 비즈니스 사유 명시

## ✅ 확인 사항

### VCN 생성 전 체크리스트
- [ ] 기존 VCN 개수 확인
- [ ] 사용하지 않는 리소스 정리
- [ ] CIDR 블록 충돌 확인
- [ ] DNS 설정 확인
- [ ] 보안 리스트 규칙 설정

### 생성 후 확인
- [ ] VCN 상태: Available
- [ ] 서브넷 연결 확인
- [ ] Internet Gateway 연결
- [ ] 보안 리스트 규칙 적용
- [ ] 인스턴스 네트워크 연결 테스트

## 📞 추가 지원

### 문제 지속 시
1. **Oracle Cloud Support** 문의
2. **Community Forum** 활용
3. **Documentation** 참조
4. **Live Chat** 지원

### 유용한 링크
- [Oracle Cloud Networking Documentation](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm)
- [Service Limits Documentation](https://docs.oracle.com/en-us/iaas/Content/General/Concepts/servicelimits.htm)
- [Free Tier Documentation](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm) 