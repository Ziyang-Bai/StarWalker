#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
// Constants
#define DELT_T1 0.5
#define DELT_T2 0.05

// Event names
const char* event[3][5] = {
    { "", "下弦月", "新　月", "满　月", "上弦月" },
    { "", "西大距", "上　合", "东大距", "下　合" },
    { "", "冲  日", "西方照", "东方照", "上　合" }
};

// Body names
const char* body[12] = {
    "太阳系质心", "水星", "金星", "地球质心", "火星", "木星", "土星", "天王星", "海王星", "冥王星", "日", "月"
};

// Function prototypes
double celestial_coor(double jd, int n, double* lon, double* lat, double* ra, double* dec);
int east_west_angle(double a1, double a2);
int east_west(double jd, int m, int n);
double included_angle(double jd, int m, int n);
double lon_angle(double jd, int m, int n, int k);
int dangle(double jd, int m, int n);
int status(double jd, int m, int n);
double iteration(double jd, int m, int n, int (*sta)(double, int, int));
double next_astro_phenomenon(double jd, int m, int n);
void event_time(double jd, int m, int n, int num);
int retrograde(double jd, int m, int n);
double next_retrograde(double jd, int n);
void retrograde_time(double jd, int n, int num);

int main() {
    double jd = 2451545.0; // Example Julian date
    event_time(jd, 5, 6, 3); // Calculate future 3 Jupiter-Saturn conjunctions
    event_time(jd, 2, 301, 4); // Calculate future 4 Venus-Moon conjunctions
    event_time(jd, 2, 10, 5); // Calculate future 5 Venus-related events
    event_time(jd, 4, 10, 6); // Calculate future 6 Mars-related events
    event_time(jd, 301, 10, 6); // Calculate future 7 Moon phase events
    retrograde_time(jd, 1, 8); // Calculate future 8 Mercury retrograde start/end times
    return 0;
}

// Function implementations
double celestial_coor(double jd, int n, double* lon, double* lat, double* ra, double* dec) {
    // Placeholder for actual celestial coordinate calculation
    *lon = 0.0;
    *lat = 0.0;
    *ra = 0.0;
    *dec = 0.0;
    return 0.0;
}

int east_west_angle(double a1, double a2) {
    if (fabs(a1 - a2) < M_PI) {
        return a2 < a1 ? 1 : 0;
    } else {
        return a2 < a1 ? 0 : 1;
    }
}

int east_west(double jd, int m, int n) {
    double lon1, lat1, ra1, dec1;
    double lon2, lat2, ra2, dec2;
    celestial_coor(jd, m == 10 ? 10 : m, &lon1, &lat1, &ra1, &dec1);
    celestial_coor(jd, n == 10 ? n : m, &lon2, &lat2, &ra2, &dec2);
    return east_west_angle(lon1, lon2);
}

double included_angle(double jd, int m, int n) {
    double lon1, lat1, ra1, dec1;
    double lon2, lat2, ra2, dec2;
    celestial_coor(jd, m, &lon1, &lat1, &ra1, &dec1);
    celestial_coor(jd, n, &lon2, &lat2, &ra2, &dec2);
    return acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon2 - lon1));
}

double lon_angle(double jd, int m, int n, int k) {
    double lon1, lat1, ra1, dec1;
    double lon2, lat2, ra2, dec2;
    celestial_coor(jd, m, &lon1, &lat1, &ra1, &dec1);
    celestial_coor(jd, n, &lon2, &lat2, &ra2, &dec2);
    double angle1 = k == 0 ? lon1 : ra1;
    double angle2 = k == 0 ? lon2 : ra2;
    if (fabs(angle1 - angle2) < M_PI) {
        return fabs(angle1 - angle2);
    } else {
        return 2 * M_PI - fabs(angle1 - angle2);
    }
}

int dangle(double jd, int m, int n) {
    double a1 = included_angle(jd, m, n) * 180.0 / M_PI;
    double a2 = included_angle(jd + DELT_T2 / 86400.0, m, n) * 180.0 / M_PI;
    double e1 = lon_angle(jd, m, n, 0) * 180.0 / M_PI;
    double e2 = lon_angle(jd + DELT_T2 / 86400.0, m, n, 0) * 180.0 / M_PI;
    if (a1 > 10.0) {
        return a1 < a2 ? 1 : 0;
    } else {
        return e1 < e2 ? 1 : 0;
    }
}

int status(double jd, int m, int n) {
    int ew = east_west(jd, m, n);
    int da = dangle(jd, m, n);
    if (m == 10 || n == 10) {
        if (ew == 1 && da == 1) return 1;
        if (ew == 1 && da == 0) return 2;
        if (ew == 0 && da == 1) return 3;
        if (ew == 0 && da == 0) return 4;
    } else {
        return ew;
    }
    return 0;
}

double iteration(double jd, int m, int n, int (*sta)(double, int, int)) {
    int s1 = sta(jd, m, n);
    int s0 = s1;
    double dt = 7.0;
    while (1) {
        jd += dt;
        int s = sta(jd, m, n);
        if (s0 != s) {
            s0 = s;
            dt = -dt / 2;
        }
        if (fabs(dt) < DELT_T1 / 86400.0 && s != s1) {
            break;
        }
    }
    return jd;
}

double next_astro_phenomenon(double jd, int m, int n) {
    return iteration(jd, m, n, status);
}

void event_time(double jd, int m, int n, int num) {
    int i = (m == 301 || n == 301) ? 0 : ((m == 1 || n == 1 || m == 2 || n == 2) ? 1 : 2);
    for (int k = 0; k < num; k++) {
        int s = status(jd, m, n);
        jd = next_astro_phenomenon(jd, m, n);
        if (i == 0) {
            printf("%s：%f\n", event[i][s], jd);
        } else if (i == 1 && (s == 1 || s == 3)) {
            double a = included_angle(jd, m, n) * 180.0 / M_PI;
            printf("%s%s：%f 夹角：%f\n", body[n], event[i][s], jd, a);
        } else {
            printf("%s%s：%f\n", body[n], event[i][s], jd);
        }
    }
}

int retrograde(double jd, int m, int n) {
    double lon1, lat1, ra1, dec1;
    double lon2, lat2, ra2, dec2;
    celestial_coor(jd, n, &lon1, &lat1, &ra1, &dec1);
    celestial_coor(jd + DELT_T2 / 86400.0, n, &lon2, &lat2, &ra2, &dec2);
    return east_west_angle(ra1, ra2);
}

double next_retrograde(double jd, int n) {
    return iteration(jd, 0, n, retrograde);
}

void retrograde_time(double jd, int n, int num) {
    int s = retrograde(jd, 0, n);
    if (s == 0) {
        printf("此刻%f%s在顺行\n", jd, body[n]);
    } else {
        printf("此刻%f%s在逆行\n", jd, body[n]);
    }
    for (int i = 0; i < num; i++) {
        s = retrograde(jd, 0, n);
        jd = next_retrograde(jd, n);
        if (s == 0) {
            printf("%s逆行开始时间：%f\n", body[n], jd);
        } else {
            printf("%s逆行结束时间：%f\n", body[n], jd);
        }
    }
}


 