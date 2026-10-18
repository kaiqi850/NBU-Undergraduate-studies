def match(target, show=True):
    target_path = target.split("-")[0]
    target_name = target.split("-")[1]
    # 防止截全屏的页面没反应过来
    time.sleep(1)
    ttime_s = time.time()

    global root_dir
    appname = root_dir + '/APP_Action_Icons/'+target_path+"/"+target_name+'.png'
    appname_2 = root_dir + '/APP_Action_Icons/'+target_path+"/"+target_name+'_2.png'
    appname_3 = root_dir + '/APP_Action_Icons/'+target_path+"/"+target_name+'_3.png'
    print(appname)
    print("root_dir =", root_dir)

    ##根据桌面路径进行截屏
    hwnd = win32gui.FindWindow(None, root_dir)
    app = QApplication(sys.argv)
    screen = QApplication.primaryScreen()
    img = screen.grabWindow(hwnd).toImage()

    ##保存截屏
    root_desk = root_dir + '/Screen_Shots/Test_Screen_shots/desktop.jpg'
    img.save(root_desk)
    ##等待图片保存
    time.sleep(0.5)
    # 支持图片名为中英文名，也支持路径中英文
    imsrc = cv2.imdecode(np.fromfile(root_desk, dtype=np.uint8), -1)
    imobj = cv2.imdecode(np.fromfile(appname, dtype=np.uint8), -1)

    ##根踞名称匹配截图，只支持图片为英文名
    # imsrc = ac.imread(root_desk)
    # imobj = ac.imread(appname)

    # 匹配图标位置
    pos = ac.find_template(imsrc, imobj, 0.5,bgremove=True)
    if pos == None and os.path.exists(appname_2):
        print("第一张图标没匹配到，现匹配第二张：", end="")
        print(appname_2)
        imobj_2 = cv2.imdecode(np.fromfile(appname_2, dtype=np.uint8), -1)
        # imobj_2 = ac.imread(appname_2)
        pos = ac.find_template(imsrc, imobj_2, 0.5,bgremove=True)
    if pos == None and os.path.exists(appname_3):
        print("第二张图标没匹配到，现匹配第三张：", end="")
        print(appname_3)
        imobj_3 = cv2.imdecode(np.fromfile(appname_3, dtype=np.uint8), -1)
        # imobj_3 = ac.imread(appname_3)
        pos = ac.find_template(imsrc, imobj_3, 0.5,bgremove=True)

    # 如果第三张还未匹配到，用另一种方法重新截图
    if pos == None:
        print("2秒后重新截全屏...")
        time.sleep(2)

        ##保存截屏
        root_desk = root_dir + '/Screen_Shots/Test_Screen_shots/desktop_2.jpg'
        img = ImageGrab.grab()
        img.save(root_desk)
        ##等待图片保存
        time.sleep(0.5)
        # 支持图片名为中英文名，也支持路径中英文
        imsrc = cv2.imdecode(np.fromfile(root_desk, dtype=np.uint8), -1)
        imobj = cv2.imdecode(np.fromfile(appname, dtype=np.uint8), -1)


        # 匹配图标位置
        pos = ac.find_template(imsrc, imobj, 0.5,bgremove=True)
        if pos == None and os.path.exists(appname_2):
            print("第一张图标没匹配到，现匹配第二张：", end="")
            print(appname_2)
            imobj_2 = cv2.imdecode(np.fromfile(appname_2, dtype=np.uint8), -1)
            pos = ac.find_template(imsrc, imobj_2, 0.5,bgremove=True)
        if pos == None and os.path.exists(appname_3):
            print("第二张图标没匹配到，现匹配第三张：", end="")
            print(appname_3)
            imobj_3 = cv2.imdecode(np.fromfile(appname_3, dtype=np.uint8), -1)
            pos = ac.find_template(imsrc, imobj_3, 0.5,bgremove=True)

    if pos == None:
        print("最终没能匹配到：" + target)
    else:
        ttime_e = time.time()
        __time = ttime_e - ttime_s

        if show == True:
            try:
                show_and_save(root_desk, target, pos, __time)
            except Exception as e:
                print("保存匹配结果show_and_save这里出错，错误原因为{}".format(e))
        print(pos)
        point = pos['result']
        pyautogui.moveTo(point)
        print("匹配成功：{}".format(target))
        time.sleep(0.5)
        print(pyautogui.position())
        pyautogui.click(clicks=2)
        return point
