import robot

def lrf_calibration( self, bot ):
    '''
        instruction:
            mettre le robot contre un mur a la perpendiculaire
    @param bot: robot
    @type bot: robot.Robot
    '''
    bot.pile.clear()
    bot.pile_resultat.clear()
    bot.add_to_pile( bot.prop.avancer_mm, ( -100, True ) ) #100
    bot.add_to_pile( bot.vue.get_range )
    bot.add_to_pile( bot.prop.avancer_mm, ( -100, True ) ) #200
    bot.add_to_pile( bot.vue.get_range )
    bot.add_to_pile( bot.prop.avancer_mm, ( -150, True ) ) #350
    bot.add_to_pile( bot.vue.get_range )
    bot.add_to_pile( bot.prop.avancer_mm, ( -150, True ) ) #500
    bot.add_to_pile( bot.vue.get_range )
    bot.add_to_pile( bot.prop.avancer_mm, ( -200, True ) ) #700
    bot.add_to_pile( bot.vue.get_range )
    bot.add_to_pile( bot.prop.avancer_mm, ( -200, True ) ) #900
    bot.add_to_pile( bot.vue.get_range )
    bot.add_to_pile( bot.prop.avancer_mm, ( -150, True ) ) #1050
    bot.add_to_pile( bot.vue.get_range )
    bot.add_to_pile( bot.prop.avancer_mm, ( -150, True ) ) #1200
    bot.add_to_pile( bot.vue.get_range )

