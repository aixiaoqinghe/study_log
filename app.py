

from flask import Flask,request,render_template
import os
import time

# 明确指定templates文件夹路径
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

@app.route("/",methods=['GET','POST'])
def home():
    result = ''
    user_input = ''
    if request.method == "POST":
        user_input = request.form.get('user_input')
        result = f"你提交的内容是：{user_input}"
    
    #Flask会自动在templates文件夹中查找模板
    return render_template('home.html',result=result,user_input=user_input)


@app.route("/save",methods=['GET','POST'])
def save():
    #用于调试
    print(f"请求方法：{request.method}")
    print(f"表单数据：{request.form}")
    #从表单中获取数据
    user_input = request.form.get("user_input")
    print(f"获取到的用户输入: {user_input}")


    if user_input:
        try:
            #使用绝对路径确保文件保存位置正确
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'notes.txt')
            print(f"保存文件路径: {file_path}")
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # 确保内容不包含分隔符，避免格式混乱
            clean_content = user_input.replace('|||', '｜｜｜')  # 替换为全角分隔符
            
            with open(file_path,'a',encoding="utf-8") as file:
                # 使用特殊分隔符将时间和内容分开，方便后续解析
                # 存储格式：内容|||创建时间
                file.write(f"{clean_content}|||{current_time}\n")
            message = f"保存成功，文件已保存至:{file_path}"
            return render_template('save_result.html',message=message,is_success=True)
        except Exception as e:
            print(f"保存错误: {str(e)}")
            message = f"保存失败:{str(e)}"
            return render_template('save_result.html',message=message,is_success=False)
    else:
        message = "没有内容需要保存"
        return render_template('save_result.html',message=message,is_success=False)


@app.route("/view",methods=['GET','POST'])
def view():
    try:
        # 使用与save函数相同的绝对路径确保文件位置正确
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notes.txt')

        #检查文件是否存在
        if not os.path.exists(file_path):
            return render_template("view.html",content="<个人学习足迹记录薄>不存在",file_exists=False)
        
        notes = []
        with open(file_path,'r',encoding='utf-8') as file:
            lines = file.read().splitlines()  # 分割成行但不包含换行符
            for line in lines:
                # 解析每一行，分离内容和时间戳
                    if '|||' in line:
                        if line.count('|||') >= 2:
                            # 新格式：内容|||创建时间|||更新时间
                            parts = line.split('|||', 2)
                            content_part = parts[0]
                            create_time = parts[1]
                            update_time = parts[2]
                            notes.append({'content':content_part,'create_time':create_time,'update_time':update_time})
                        else:
                            # 旧格式：内容|||时间
                            content_part,time_part = line.split('|||',1)
                            notes.append({'content':content_part,'create_time':time_part,'update_time':time_part})
                    else:
                        # 处理没有时间戳的旧格式
                        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
                        notes.append({'content':line,'create_time':current_time,'update_time':current_time})
        return render_template("view.html",notes = notes,file_exists=True)
    except Exception as e:
        print(f"读取文件错误：{str(e)}")
        return render_template("view.html",content="读取文件失败",file_exists=False)


@app.route("/delete",methods=['POST'])
def delete():
    try:
        # 获取文件路径
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notes.txt')

        #读取所有行
        with open(file_path,'r',encoding='utf-8') as file:
            lines = file.read().splitlines()

        #获取选中的行索引
        selected_indices = request.form.getlist('selected_notes')
        selected_indices = [int(index) for index in selected_indices]

        #直接过滤掉选中的行
        #保留未选中的行
        filtered_lines = [line for i,line in enumerate(lines) if i not in selected_indices]

        #将过滤后的内容写回文件
        with open(file_path,'w',encoding='utf-8') as file:
            for line in filtered_lines:
                file.write(line + '\n')

        #重定向回查看页面，显示删除成功消息
        return render_template('view.html',message='删除成功',file_exists=True,notes=get_notes_from_file())
    except Exception as e:
        print(f"删除错误:{str(e)}")
        return render_template("view.html",content=f"删除失败：{str(e)}",file_exists=False)
    
#添加一个辅助函数来获取笔记
def get_notes_from_file():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notes.txt')
    notes = []

    #检查文件是否存在
    if os.path.exists(file_path):
        with open(file_path,'r',encoding='utf-8') as file:
            lines = file.read().splitlines()
            for line in lines:
                # 解析每一行，分离内容和时间戳
                try:
                    if '|||' in line:
                        # 安全解析，计算分隔符数量
                        separator_count = line.count('|||')
                        
                        if separator_count >= 2:
                            # 新格式：内容|||创建时间|||更新时间
                            parts = line.split('|||', 2)
                            # 确保有足够的部分
                            if len(parts) >= 3:
                                content_part = parts[0]
                                create_time = parts[1]
                                update_time = parts[2]
                                notes.append({'content':content_part,'create_time':create_time,'update_time':update_time})
                            else:
                                # 部分格式错误，尝试基本解析
                                parts = line.split('|||', 1)
                                if len(parts) >= 2:
                                    content_part = parts[0]
                                    time_part = parts[1]
                                    notes.append({'content':content_part,'create_time':time_part,'update_time':time_part})
                                else:
                                    # 格式完全错误，使用整行作为内容
                                    notes.append({'content':line,'create_time':time.strftime("%Y-%m-%d %H:%M:%S"),'update_time':time.strftime("%Y-%m-%d %H:%M:%S")})
                        else:
                            # 旧格式：内容|||时间
                            parts = line.split('|||', 1)
                            if len(parts) >= 2:
                                content_part = parts[0]
                                time_part = parts[1]
                                notes.append({'content':content_part,'create_time':time_part,'update_time':time_part})
                            else:
                                # 格式错误，使用整行作为内容
                                notes.append({'content':line,'create_time':time.strftime("%Y-%m-%d %H:%M:%S"),'update_time':time.strftime("%Y-%m-%d %H:%M:%S")})
                    else:
                        # 处理没有时间戳的旧格式
                        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
                        notes.append({'content':line,'create_time':current_time,'update_time':current_time})
                except Exception as e:
                    # 捕获任何解析错误，确保程序继续运行
                    print(f"解析行时出错: {str(e)}, 行内容: {line}")
                    notes.append({'content':line,'create_time':time.strftime("%Y-%m-%d %H:%M:%S"),'update_time':time.strftime("%Y-%m-%d %H:%M:%S")})
    return notes


@app.route("/edit",methods=['POST'])
def edit():
    try:
        #获取文件路径
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'notes.txt')

        #读取所有行
        with open(file_path,'r',encoding='utf-8') as file:
            lines = file.read().splitlines()

        #获取要修改的索引和新内容
        edit_index = int(request.form.get('edit_index'))
        new_content = request.form.get('edit_content')

        #检查索引是否有效
        if 0 <= edit_index < len(lines):
            #解析原行，保留创建时间
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            create_time = current_time  # 默认使用当前时间作为创建时间
            
            # 安全解析原行，避免格式错误
            if '|||' in lines[edit_index]:
                # 计算分隔符数量
                separator_count = lines[edit_index].count('|||')
                
                if separator_count >= 2:
                    # 新格式：内容|||创建时间|||更新时间
                    parts = lines[edit_index].split('|||', 2)
                    # 确保至少有两个部分
                    if len(parts) >= 2:
                        create_time = parts[1]
                else:
                    # 旧格式：内容|||时间
                    parts = lines[edit_index].split('|||', 1)
                    if len(parts) >= 2:
                        create_time = parts[1]

            #创建新的行内容，保留创建时间，更新修改时间
            # 确保新内容不包含分隔符，避免格式混乱
            clean_content = new_content.replace('|||', '｜｜｜')  # 替换为全角分隔符
            new_line = f"{clean_content}|||{create_time}|||{current_time}"
            lines[edit_index] = new_line

            #将修改后的内容写回文件
            with open(file_path,'w',encoding='utf-8') as file:
                for line in lines:
                    file.write(line + '\n')

            #重定向回查看页面，显示修改成功消息
            return render_template('view.html',message='修改成功',file_exists=True,notes=get_notes_from_file())
        else: 
            return render_template('view.html',content="索引无效",file_exists=True,notes=get_notes_from_file())
    except Exception as e:
        print(f"修改错误:{str(e)}")
        return render_template("view.html",content=f"修改失败：{str(e)}",file_exists=False)

                                 




if __name__ == "__main__":
    app.run(debug=True)