# -*- coding: utf-8 -*-
###########################################################################################
#
#    module name for OpenERP
#    Copyright (C) 2015 qdodoo Technology CO.,LTD. (<http://www.qdodoo.com/>).
#
###########################################################################################

{
    'name' : 'Qdodoo 定期保存数据',    #模块名称
    'version' : '1.0',    #版本
    'category' : 'Technology',    #分类
    'author' : 'qdodoo Technology',    #作者
    'website': 'http://www.qdodoo.com/',    #网址
    'summary': '',    #摘要
    'images' : [],    #模块图片
    'depends' : ['base'],    #依赖模块
    'data': [
        'data/qdodoo_previous_balance.xml',
        # ...
    ],    #更新XML,CSV
    'js': [
        # 'static/src/js/account_move_reconciliation.js',
        # ...
    ],    #javascript
    'qweb' : [
        # "static/src/xml/account_move_reconciliation.xml",
        # ...
    ],
    'css':[
        # 'static/src/css/account_move_reconciliation.css',
        # ...
    ],    #css样式
    'demo': [
        # 'demo/account_demo.xml',
        # ...
    ],
    'test': [
        # 'test/account_customer_invoice.yml',
        # ...
    ],    #测试
    'application': True,    #是否认证
    'installable': True,    #是否可安装
    'auto_install': False,    #是否自动安装
    'description' : """
    1：每天物品明细账前期结余的数据
    2：每月保存科目余额表数据
    """,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: