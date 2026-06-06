import type { Locale } from "./config";

export interface Dictionary {
    common: {
        home: string;
        chapters: string;
        wiki: string;
        leaderboard: string;
        map: string;
        headquarters: string;
        guide: string;
        readNow: string;
        profile: string;
        login: string;
        logout: string;
        latestChapter: string;
        online: string;
        fallbackVietnamese: string;
        language: string;
    };
    header: {
        archive: string;
    };
    footer: {
        heading: string;
        links: string;
        stats: string;
        latest: string;
        firstChapter: string;
        allRightsReserved: string;
        author: string;
        status: string;
        genres: string;
        chapters: string;
        blurb: string;
    };
    reader: {
        chapter: string;
        toc: string;
        previous: string;
        next: string;
        start: string;
        end: string;
        save: string;
        saved: string;
        shareStory: string;
        leaveALike: string;
        previousChapter: string;
        nextChapter: string;
        home: string;
        quickFallback: string;
        continueReading: string;
        jumpPlaceholder: string;
        jumpAction: string;
    };
    audio: {
        title: string;
        playing: string;
        paused: string;
        stopped: string;
        play: string;
        pause: string;
        resume: string;
        replay: string;
        skip: string;
        changeChapter: string;
        keepScreenOn: string;
        floatingTitle: string;
        speed: string;
        shortcuts: string;
    };
    lookup: {
        action: string;
        title: string;
        selected: string;
        loading: string;
        empty: string;
        failed: string;
        close: string;
        external: string;
        hint: string;
    };
    oracle: {
        title: string;
        scope: string;
        antiSpoiler: string;
        placeholder: string;
        submit: string;
        quickPrompts: string[];
        readyMessage: (chapter: number) => string;
        backendOffline: string;
        unknownError: string;
        invalidResponse: string;
        sources: Record<string, string>;
        diagnostics: Record<string, string>;
        feedbackBtn: string;
        feedbackTitle: string;
        feedbackTypes: Record<string, string>;
        feedbackCommentPlaceholder: string;
        feedbackCorrectionPlaceholder: string;
        feedbackSubmit: string;
        feedbackCancel: string;
        feedbackSuccess: string;
        feedbackError: string;
    };
    tooltip: {
        title: string;
        loading: string;
        notFound: string;
        name: string;
        faction: string;
        status: string;
        ability: string;
        firstAppearance: string;
        chapter: string;
    };
    home: {
        latest: string;
        latestDesc: string;
        seeAll: string;
        startNow: string;
        author: string;
        chapters: string;
        genres: string;
        status: string;
        latestPublished: string;
        latestUpdated: string;
        readFirst: string;
        viewContents: string;
    };
    headquarters: {
        title: string;
        subtitle: string;
        chapter: string;
        loading: string;
        resources: string;
        personnel: string;
        infrastructure: string;
        recent: string;
        feed: string;
        syncError: string;
        food: string;
        crystals: string;
        water: string;
        warriors: string;
        researchers: string;
        civilians: string;
        walls: string;
        territory: string;
        morale: string;
        latestCheckpoint: string;
        spoilerSafe: string;
    };
    hud: {
        title: string;
        dangerLevel: string;
        bioMonitor: string;
        mcStatus: string;
        quickScan: string;
        chapter: string;
        readProgress: string;
        sysUplink: string;
        minimize: string;
        expand: string;
        st_normal: string;
        st_injured: string;
        st_mutated: string;
        st_critical: string;
    };
}

export const dictionaries: Record<Locale, Dictionary> = {
    vi: {
        common: {
            home: "Trang chủ",
            chapters: "Mục lục",
            wiki: "Bách khoa",
            leaderboard: "Bảng xếp hạng",
            map: "Bản đồ",
            headquarters: "Sở chỉ huy",
            guide: "Hướng dẫn",
            readNow: "Đọc ngay",
            profile: "Hồ sơ",
            login: "Đăng nhập",
            logout: "Đăng xuất",
            latestChapter: "Chương mới nhất",
            online: "Trực tuyến",
            fallbackVietnamese: "Đang dùng bản tiếng Việt",
            language: "Ngôn ngữ",
        },
        header: {
            archive: "Kho truyện",
        },
        footer: {
            heading: "Mạt Thế",
            links: "Điều hướng",
            stats: "Thông tin truyện",
            latest: "Chương mới nhất",
            firstChapter: "Chương đầu",
            allRightsReserved: "Bảo lưu mọi quyền",
            author: "Tác giả",
            status: "Tình trạng",
            genres: "Thể loại",
            chapters: "Số chương",
            blurb: "Theo chân Hàn Phong trong hành trình sinh tồn giữa tận thế sinh hóa.",
        },
        reader: {
            chapter: "Chương",
            toc: "Mục lục",
            previous: "Trước",
            next: "Tiếp",
            start: "Đầu",
            end: "Cuối",
            save: "Lưu trang",
            saved: "Đã lưu",
            shareStory: "Chia sẻ truyện",
            leaveALike: "Thích chương này? Để lại một tim nhé.",
            previousChapter: "Chương trước",
            nextChapter: "Chương tiếp",
            home: "Trang chủ",
            quickFallback: "Bản dịch chưa sẵn sàng, hệ thống đang hiển thị tiếng Việt.",
            continueReading: "Đọc tiếp",
            jumpPlaceholder: "Số chương hoặc từ khóa...",
            jumpAction: "Đi",
        },
        audio: {
            title: "Nghe truyện",
            playing: "Đang phát...",
            paused: "Tạm dừng",
            stopped: "Dừng",
            play: "Phát",
            pause: "Tạm dừng",
            resume: "Tiếp tục",
            replay: "Nghe lại",
            skip: "Đoạn kế",
            changeChapter: "Chuyển chương",
            keepScreenOn: "Tắt màn hình vẫn nghe được",
            floatingTitle: "Điều khiển audio",
            speed: "Tốc độ",
            shortcuts: "Phím tắt: Alt+P phát/tạm dừng, Alt+S dừng, Alt+[ lùi đoạn, Alt+] tới đoạn",
        },
        lookup: {
            action: "Tra nhanh",
            title: "Tra từ trong trang",
            selected: "Từ/cụm đã chọn",
            loading: "AI đang giải nghĩa...",
            empty: "Chọn một từ hoặc cụm ngắn trong đoạn để tra ngay mà không rời trang.",
            failed: "Chưa tra được lúc này. Hãy thử lại sau.",
            close: "Đóng",
            external: "Mở từ điển chuyên sâu",
            hint: "Bôi đen một từ hoặc cụm ngắn để tra nhanh.",
        },
        oracle: {
            title: "AI Oracle",
            scope: "Phạm vi",
            antiSpoiler: "Chống spoiler ON",
            placeholder: "Đặt câu hỏi cho Hệ Thống...",
            submit: "Gửi",
            quickPrompts: ["Hàn Phong là ai?", "Thế lực nào xuất hiện sau chương này?"],
            readyMessage: (chapter) =>
                `[HỆ THỐNG ĐÃ KẾT NỐI]\nTiến trình đọc hiện tại: Chương ${chapter}.\nTôi chỉ hiển thị thông tin nằm trong phạm vi spoiler an toàn của bạn.`,
            backendOffline: "[CHẨN ĐOÁN HỆ THỐNG]\nKhông thể kết nối Oracle backend.",
            unknownError: "Oracle chưa thể trả lời lúc này. Hãy thử lại sau.",
            invalidResponse: "Không nhận được phản hồi hợp lệ.",
            sources: {
                cache: "Bộ nhớ cache",
                local_wiki: "Bách khoa nội bộ",
                gemini: "AI Oracle",
                ai_provider: "AI Oracle",
            },
            diagnostics: {
                ready: "ONLINE",
                processing: "ĐANG XỬ LÝ",
                backend_offline: "BACKEND OFFLINE",
                missing_api_key: "THIẾU API KEY",
                rate_limited: "RATE LIMITED",
                model_exhausted: "MODEL EXHAUSTED",
                invalid_question: "INPUT KHÔNG HỢP LỆ",
                backend_error: "BACKEND ERROR",
            },
            feedbackBtn: "Báo lỗi câu trả lời",
            feedbackTitle: "Báo lỗi câu trả lời RAG",
            feedbackTypes: {
                wrong: "Sai kiến thức",
                missing: "Thiếu thông tin",
                spoiler: "Lộ tình tiết/spoiler",
                hallucination: "AI bịa",
                other: "Khác"
            },
            feedbackCommentPlaceholder: "Góp ý của bạn về câu trả lời...",
            feedbackCorrectionPlaceholder: "Đề xuất sửa đổi thông tin đúng (nếu có)...",
            feedbackSubmit: "Gửi phản hồi",
            feedbackCancel: "Hủy",
            feedbackSuccess: "Đã gửi góp ý. Cảm ơn bạn đã giúp cải thiện AI.",
            feedbackError: "Chưa gửi được góp ý. Vui lòng thử lại.",
        },
        tooltip: {
            title: "QUICK SCAN",
            loading: "Đang quét dữ liệu...",
            notFound: "Không tìm thấy dữ liệu",
            name: "Tên",
            faction: "Phe",
            status: "Trạng thái",
            ability: "Năng lực",
            firstAppearance: "Xuất hiện",
            chapter: "Chương",
        },
        home: {
            latest: "Chương mới đăng",
            latestDesc: "Cập nhật mới nhất",
            seeAll: "Xem tất cả",
            startNow: "Bắt đầu đọc",
            author: "Tác giả",
            chapters: "Chương",
            genres: "Thể loại",
            status: "Tình trạng",
            latestPublished: "Mới xuất bản",
            latestUpdated: "Cập nhật gần đây",
            readFirst: "Đọc từ đầu",
            viewContents: "Xem mục lục",
        },
        headquarters: {
            title: "Sở Chỉ Huy",
            subtitle: "Bảng điều hành nhập vai theo tiến trình chương, không lộ dữ liệu tương lai.",
            chapter: "Chương",
            loading: "Đang đồng bộ dữ liệu HQ...",
            resources: "Tài nguyên",
            personnel: "Nhân lực",
            infrastructure: "Hạ tầng",
            recent: "Mốc gần nhất",
            feed: "HEADQUARTERS FEED",
            syncError: "Không thể kết nối dữ liệu Headquarters.",
            food: "Lương thực",
            crystals: "Tinh hạch",
            water: "Nước",
            warriors: "Chiến binh",
            researchers: "Nghiên cứu",
            civilians: "Dân thường",
            walls: "Tường phòng thủ",
            territory: "Lãnh thổ",
            morale: "Sĩ khí",
            latestCheckpoint: "Dấu mốc gần nhất",
            spoilerSafe: "Dữ liệu chỉ hiển thị theo chương bạn chọn để giữ trải nghiệm spoiler-safe.",
        },
        hud: {
            title: "HỆ THỐNG",
            dangerLevel: "MỨC ĐỘ NGUY HIỂM",
            bioMonitor: "CHỈ SỐ SINH TỒN",
            mcStatus: "TRẠNG THÁI NHÂN VẬT",
            quickScan: "QUÉT NHANH",
            chapter: "CHƯƠNG",
            readProgress: "TIẾN ĐỘ ĐỌC",
            sysUplink: "SYS-UPLINK",
            minimize: "THU GỌN",
            expand: "MỞ RỘNG",
            st_normal: "BÌNH THƯỜNG",
            st_injured: "BỊ THƯƠNG",
            st_mutated: "BIẾN DỊ",
            st_critical: "NGUY KỊCH",
        },
    },
    en: {
        common: {
            home: "Home",
            chapters: "Chapters",
            wiki: "Wiki",
            leaderboard: "Leaderboard",
            map: "Map",
            headquarters: "Headquarters",
            guide: "Guide",
            readNow: "Read now",
            profile: "Profile",
            login: "Log in",
            logout: "Log out",
            latestChapter: "Latest chapter",
            online: "Online",
            fallbackVietnamese: "Showing Vietnamese fallback",
            language: "Language",
        },
        header: {
            archive: "Archive",
        },
        footer: {
            heading: "The Last Days",
            links: "Navigation",
            stats: "Novel data",
            latest: "Latest chapter",
            firstChapter: "Chapter one",
            allRightsReserved: "All rights reserved",
            author: "Author",
            status: "Status",
            genres: "Genres",
            chapters: "Chapters",
            blurb: "Follow Han Phong through a bioweapon apocalypse where survival is never clean.",
        },
        reader: {
            chapter: "Chapter",
            toc: "Contents",
            previous: "Prev",
            next: "Next",
            start: "Start",
            end: "End",
            save: "Save",
            saved: "Saved",
            shareStory: "Share story",
            leaveALike: "Enjoyed this chapter? Leave a heart.",
            previousChapter: "Previous chapter",
            nextChapter: "Next chapter",
            home: "Home",
            quickFallback: "Translation is not ready yet. Showing the Vietnamese source text.",
            continueReading: "Continue",
            jumpPlaceholder: "Chapter number or keyword...",
            jumpAction: "Go",
        },
        audio: {
            title: "Listen",
            playing: "Playing...",
            paused: "Paused",
            stopped: "Stopped",
            play: "Play",
            pause: "Pause",
            resume: "Resume",
            replay: "Replay",
            skip: "Next chunk",
            changeChapter: "Change chapter",
            keepScreenOn: "Audio keeps playing with the screen off",
            floatingTitle: "Audio controls",
            speed: "Speed",
            shortcuts: "Shortcuts: Alt+P play/pause, Alt+S stop, Alt+[ previous chunk, Alt+] next chunk",
        },
        lookup: {
            action: "Lookup",
            title: "In-page lookup",
            selected: "Selected text",
            loading: "Checking meaning...",
            empty: "Select a word or short phrase in the chapter to look it up without leaving the page.",
            failed: "Lookup is unavailable right now. Try again later.",
            close: "Close",
            external: "Open full dictionary",
            hint: "Highlight a word or short phrase for a quick lookup.",
        },
        oracle: {
            title: "AI Oracle",
            scope: "Scope",
            antiSpoiler: "Anti-spoiler ON",
            placeholder: "Ask the System...",
            submit: "Send",
            quickPrompts: ["Who is Han Phong?", "Which faction appears after this point?"],
            readyMessage: (chapter) =>
                `[SYSTEM ONLINE]\nReading progress locked at Chapter ${chapter}.\nI only reveal information inside your spoiler-safe range.`,
            backendOffline: "[SYSTEM DIAGNOSTIC]\nUnable to reach the Oracle backend.",
            unknownError: "Oracle cannot answer right now. Try again later.",
            invalidResponse: "No valid response received.",
            sources: {
                cache: "Cache memory",
                local_wiki: "Local wiki",
                gemini: "AI Oracle",
                ai_provider: "AI Oracle",
            },
            diagnostics: {
                ready: "ONLINE",
                processing: "PROCESSING",
                backend_offline: "BACKEND OFFLINE",
                missing_api_key: "MISSING API KEY",
                rate_limited: "RATE LIMITED",
                model_exhausted: "MODEL EXHAUSTED",
                invalid_question: "INVALID INPUT",
                backend_error: "BACKEND ERROR",
            },
            feedbackBtn: "Report Issue",
            feedbackTitle: "Report Answer Issue",
            feedbackTypes: {
                wrong: "Incorrect info",
                missing: "Missing info",
                spoiler: "Spoiler content",
                hallucination: "AI hallucination",
                other: "Other"
            },
            feedbackCommentPlaceholder: "Your comment about this answer...",
            feedbackCorrectionPlaceholder: "Suggested correct info (optional)...",
            feedbackSubmit: "Submit",
            feedbackCancel: "Cancel",
            feedbackSuccess: "Feedback submitted. Thank you!",
            feedbackError: "Could not submit feedback. Try again.",
        },
        tooltip: {
            title: "QUICK SCAN",
            loading: "Scanning data...",
            notFound: "No data found",
            name: "Name",
            faction: "Faction",
            status: "Status",
            ability: "Ability",
            firstAppearance: "First seen",
            chapter: "Chapter",
        },
        home: {
            latest: "Newest releases",
            latestDesc: "Latest updates",
            seeAll: "See all",
            startNow: "Start reading",
            author: "Author",
            chapters: "Chapters",
            genres: "Genres",
            status: "Status",
            latestPublished: "Just published",
            latestUpdated: "Recently updated",
            readFirst: "Read from the beginning",
            viewContents: "Browse chapters",
        },
        headquarters: {
            title: "Headquarters",
            subtitle: "A roleplay dashboard tied to chapter progress without leaking future-state data.",
            chapter: "Chapter",
            loading: "Synchronizing HQ telemetry...",
            resources: "Resources",
            personnel: "Personnel",
            infrastructure: "Infrastructure",
            recent: "Latest checkpoint",
            feed: "HEADQUARTERS FEED",
            syncError: "Unable to connect Headquarters data.",
            food: "Food",
            crystals: "Crystals",
            water: "Water",
            warriors: "Warriors",
            researchers: "Researchers",
            civilians: "Civilians",
            walls: "Defense walls",
            territory: "Territory",
            morale: "Morale",
            latestCheckpoint: "Latest checkpoint",
            spoilerSafe: "Data is capped to your selected chapter to remain spoiler-safe.",
        },
        hud: {
            title: "THE SYSTEM",
            dangerLevel: "DANGER LEVEL",
            bioMonitor: "BIO-MONITOR",
            mcStatus: "MC STATUS",
            quickScan: "QUICK SCAN",
            chapter: "CHAPTER",
            readProgress: "READ PROGRESS",
            sysUplink: "SYS-UPLINK",
            minimize: "MINIMIZE",
            expand: "EXPAND",
            st_normal: "NORMAL",
            st_injured: "INJURED",
            st_mutated: "MUTATED",
            st_critical: "CRITICAL",
        },
    },
    "zh-CN": {
        common: {
            home: "首页",
            chapters: "目录",
            wiki: "百科",
            leaderboard: "排行榜",
            map: "地图",
            headquarters: "总部",
            guide: "指南",
            readNow: "立即阅读",
            profile: "个人资料",
            login: "登录",
            logout: "退出",
            latestChapter: "最新章节",
            online: "在线",
            fallbackVietnamese: "当前显示越南语原文",
            language: "语言",
        },
        header: {
            archive: "档案库",
        },
        footer: {
            heading: "末世",
            links: "导航",
            stats: "作品信息",
            latest: "最新章节",
            firstChapter: "第一章",
            allRightsReserved: "保留所有权利",
            author: "作者",
            status: "状态",
            genres: "题材",
            chapters: "章节数",
            blurb: "跟随韩风走进生化末世，在崩坏秩序中挣扎求生。",
        },
        reader: {
            chapter: "第",
            toc: "目录",
            previous: "上一章",
            next: "下一章",
            start: "开头",
            end: "结尾",
            save: "保存",
            saved: "已保存",
            shareStory: "分享作品",
            leaveALike: "喜欢这一章的话，留下一个心吧。",
            previousChapter: "上一章",
            nextChapter: "下一章",
            home: "首页",
            quickFallback: "译文尚未就绪，系统正在显示越南语原文。",
            continueReading: "继续阅读",
            jumpPlaceholder: "章节号或关键词...",
            jumpAction: "前往",
        },
        audio: {
            title: "听书",
            playing: "播放中...",
            paused: "已暂停",
            stopped: "已停止",
            play: "播放",
            pause: "暂停",
            resume: "继续",
            replay: "重听",
            skip: "下一段",
            changeChapter: "切换章节",
            keepScreenOn: "锁屏后仍可继续播放",
            floatingTitle: "音频控制",
            speed: "速度",
            shortcuts: "快捷键：Alt+P 播放/暂停，Alt+S 停止，Alt+[ 上一段，Alt+] 下一段",
        },
        lookup: {
            action: "速查",
            title: "页内查词",
            selected: "已选文本",
            loading: "正在解析词义...",
            empty: "选中一个词或短语，即可在当前页面快速查义。",
            failed: "暂时无法查词，请稍后再试。",
            close: "关闭",
            external: "打开完整词典",
            hint: "选中文中的一个词或短语即可速查。",
        },
        oracle: {
            title: "AI Oracle",
            scope: "范围",
            antiSpoiler: "防剧透已开启",
            placeholder: "向系统提问...",
            submit: "发送",
            quickPrompts: ["韩风是谁？", "后面会出现哪些势力？"],
            readyMessage: (chapter) =>
                `[系统在线]\n当前阅读进度已锁定在第 ${chapter} 章。\n我只会回答你当前无剧透范围内的信息。`,
            backendOffline: "[系统诊断]\n无法连接 Oracle 后端。",
            unknownError: "Oracle 当前无法作答，请稍后再试。",
            invalidResponse: "未收到有效响应。",
            sources: {
                cache: "缓存",
                local_wiki: "本地百科",
                gemini: "AI Oracle",
                ai_provider: "AI Oracle",
            },
            diagnostics: {
                ready: "ONLINE",
                processing: "处理中",
                backend_offline: "BACKEND OFFLINE",
                missing_api_key: "缺少 API KEY",
                rate_limited: "RATE LIMITED",
                model_exhausted: "MODEL EXHAUSTED",
                invalid_question: "输入无效",
                backend_error: "BACKEND ERROR",
            },
            feedbackBtn: "报告错误",
            feedbackTitle: "报告回答错误",
            feedbackTypes: {
                wrong: "信息有误",
                missing: "信息缺失",
                spoiler: "剧透内容",
                hallucination: "AI幻觉",
                other: "其他"
            },
            feedbackCommentPlaceholder: "您对该回答的反馈意见...",
            feedbackCorrectionPlaceholder: "建议的正确信息（可选）...",
            feedbackSubmit: "提交",
            feedbackCancel: "取消",
            feedbackSuccess: "反馈已提交。谢谢！",
            feedbackError: "无法提交反馈。请重试。",
        },
        tooltip: {
            title: "快速扫描",
            loading: "正在扫描数据...",
            notFound: "未找到数据",
            name: "姓名",
            faction: "阵营",
            status: "状态",
            ability: "能力",
            firstAppearance: "首次出现",
            chapter: "章节",
        },
        home: {
            latest: "最新发布",
            latestDesc: "最近更新",
            seeAll: "查看全部",
            startNow: "开始阅读",
            author: "作者",
            chapters: "章节",
            genres: "题材",
            status: "状态",
            latestPublished: "刚刚发布",
            latestUpdated: "最近更新",
            readFirst: "从第一章开始",
            viewContents: "浏览目录",
        },
        headquarters: {
            title: "总部",
            subtitle: "与章节进度绑定的指挥面板，不会泄露未来信息。",
            chapter: "章节",
            loading: "正在同步总部数据...",
            resources: "资源",
            personnel: "人员",
            infrastructure: "基础设施",
            recent: "最近检查点",
            feed: "HEADQUARTERS FEED",
            syncError: "无法连接总部数据。",
            food: "粮食",
            crystals: "晶核",
            water: "水",
            warriors: "战士",
            researchers: "研究员",
            civilians: "平民",
            walls: "防御墙",
            territory: "领地",
            morale: "士气",
            latestCheckpoint: "最近检查点",
            spoilerSafe: "数据会限制在你选择的章节范围内，保持无剧透体验。",
        },
        hud: {
            title: "系统",
            dangerLevel: "危险等级",
            bioMonitor: "生命体征",
            mcStatus: "主角状态",
            quickScan: "快速扫描",
            chapter: "章节",
            readProgress: "阅读进度",
            sysUplink: "系统上行",
            minimize: "折叠",
            expand: "展开",
            st_normal: "正常",
            st_injured: "受伤",
            st_mutated: "变异",
            st_critical: "危急",
        },
    },
    ja: {
        common: {
            home: "ホーム",
            chapters: "目次",
            wiki: "百科",
            leaderboard: "ランキング",
            map: "マップ",
            headquarters: "司令部",
            guide: "ガイド",
            readNow: "今すぐ読む",
            profile: "プロフィール",
            login: "ログイン",
            logout: "ログアウト",
            latestChapter: "最新話",
            online: "オンライン",
            fallbackVietnamese: "現在はベトナム語原文を表示中",
            language: "言語",
        },
        header: {
            archive: "アーカイブ",
        },
        footer: {
            heading: "末世",
            links: "ナビゲーション",
            stats: "作品情報",
            latest: "最新話",
            firstChapter: "第1話",
            allRightsReserved: "All rights reserved",
            author: "作者",
            status: "状態",
            genres: "ジャンル",
            chapters: "話数",
            blurb: "韓風とともに、生化学的な終末世界での生存劇を追いかける。",
        },
        reader: {
            chapter: "第",
            toc: "目次",
            previous: "前へ",
            next: "次へ",
            start: "冒頭",
            end: "末尾",
            save: "保存",
            saved: "保存済み",
            shareStory: "共有",
            leaveALike: "この話が良ければハートを残してください。",
            previousChapter: "前の話",
            nextChapter: "次の話",
            home: "ホーム",
            quickFallback: "翻訳はまだ準備中のため、ベトナム語原文を表示しています。",
            continueReading: "続きを読む",
            jumpPlaceholder: "話数またはキーワード...",
            jumpAction: "移動",
        },
        audio: {
            title: "読み上げ",
            playing: "再生中...",
            paused: "一時停止",
            stopped: "停止",
            play: "再生",
            pause: "一時停止",
            resume: "再開",
            replay: "聞き直す",
            skip: "次の区切り",
            changeChapter: "話を切り替える",
            keepScreenOn: "画面オフでも再生を続けます",
            floatingTitle: "音声コントロール",
            speed: "再生速度",
            shortcuts: "ショートカット: Alt+P 再生/一時停止, Alt+S 停止, Alt+[ 前の区切り, Alt+] 次の区切り",
        },
        lookup: {
            action: "クイック辞書",
            title: "ページ内単語検索",
            selected: "選択した語句",
            loading: "意味を確認中...",
            empty: "単語や短いフレーズを選択すると、ページを離れずにすぐ調べられます。",
            failed: "今は検索できません。後でもう一度試してください。",
            close: "閉じる",
            external: "詳しい辞書を開く",
            hint: "語句を選択するとクイック検索できます。",
        },
        oracle: {
            title: "AI Oracle",
            scope: "範囲",
            antiSpoiler: "ネタバレ防止 ON",
            placeholder: "システムに質問する...",
            submit: "送信",
            quickPrompts: ["韓風とは誰ですか？", "この先どんな勢力が出てきますか？"],
            readyMessage: (chapter) =>
                `[システム接続完了]\n読書進行は第${chapter}話に固定されています。\n現在のネタバレ安全範囲内の情報だけを返します。`,
            backendOffline: "[システム診断]\nOracle バックエンドへ接続できません。",
            unknownError: "Oracle は今応答できません。後でもう一度試してください。",
            invalidResponse: "有効な応答を受信できませんでした。",
            sources: {
                cache: "キャッシュ",
                local_wiki: "ローカル百科",
                gemini: "AI Oracle",
                ai_provider: "AI Oracle",
            },
            diagnostics: {
                ready: "ONLINE",
                processing: "処理中",
                backend_offline: "BACKEND OFFLINE",
                missing_api_key: "API KEY 不足",
                rate_limited: "RATE LIMITED",
                model_exhausted: "MODEL EXHAUSTED",
                invalid_question: "入力エラー",
                backend_error: "BACKEND ERROR",
            },
            feedbackBtn: "問題を報告",
            feedbackTitle: "回答の不具合を報告",
            feedbackTypes: {
                wrong: "誤った情報",
                missing: "情報の不足",
                spoiler: "ネタバレ内容",
                hallucination: "AIの幻覚",
                other: "その他"
            },
            feedbackCommentPlaceholder: "この回答に対するフィードバック...",
            feedbackCorrectionPlaceholder: "正しい情報の提案（任意）...",
            feedbackSubmit: "送信",
            feedbackCancel: "キャンセル",
            feedbackSuccess: "送信完了。ご協力ありがとうございます！",
            feedbackError: "送信できませんでした。再試行してください。",
        },
        tooltip: {
            title: "クイックスキャン",
            loading: "データをスキャン中...",
            notFound: "データが見つかりません",
            name: "名前",
            faction: "勢力",
            status: "状態",
            ability: "能力",
            firstAppearance: "初登場",
            chapter: "話",
        },
        home: {
            latest: "最新更新",
            latestDesc: "直近の更新",
            seeAll: "すべて見る",
            startNow: "読み始める",
            author: "作者",
            chapters: "話数",
            genres: "ジャンル",
            status: "状態",
            latestPublished: "最新公開",
            latestUpdated: "最近の更新",
            readFirst: "最初から読む",
            viewContents: "目次を見る",
        },
        headquarters: {
            title: "司令部",
            subtitle: "章の進行に連動するロールプレイ用ダッシュボードで、未来情報は表示しません。",
            chapter: "話",
            loading: "司令部データを同期中...",
            resources: "資源",
            personnel: "人員",
            infrastructure: "インフラ",
            recent: "最新チェックポイント",
            feed: "HEADQUARTERS FEED",
            syncError: "司令部データに接続できません。",
            food: "食料",
            crystals: "結晶核",
            water: "水",
            warriors: "戦士",
            researchers: "研究員",
            civilians: "民間人",
            walls: "防壁",
            territory: "領土",
            morale: "士気",
            latestCheckpoint: "最新チェックポイント",
            spoilerSafe: "選択した話数までのデータだけを表示し、ネタバレを防ぎます。",
        },
        hud: {
            title: "システム",
            dangerLevel: "危険度",
            bioMonitor: "バイオモニター",
            mcStatus: "ステータス",
            quickScan: "クイックスキャン",
            chapter: "話",
            readProgress: "読書進捗",
            sysUplink: "システム同期",
            minimize: "最小化",
            expand: "最大化",
            st_normal: "正常",
            st_injured: "負傷",
            st_mutated: "変異",
            st_critical: "危篤",
        },
    },
};

export function getDictionary(locale: Locale): Dictionary {
    return dictionaries[locale] ?? dictionaries.vi;
}
